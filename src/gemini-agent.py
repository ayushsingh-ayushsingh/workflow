import logging
from dotenv import load_dotenv

import os
from mem0 import AsyncMemoryClient

from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
    room_io,
    ChatContext,
    ChatMessage,
    llm,
)

from livekit.plugins import (
    silero,
    noise_cancellation,
)

from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.plugins import google

# -------------------------------------------------
# Setup
# -------------------------------------------------
logger = logging.getLogger("memory-agent")
logging.basicConfig(level=logging.INFO)

load_dotenv(".env.local")

# Mem0 client
mem0_client = AsyncMemoryClient(
    api_key=os.environ["MEM0_API_KEY"]
)

# Stable user ID for memory
MEM0_USER_ID = "livekit-voice-user"


# -------------------------------------------------
# Agent with Mem0 Memory
# -------------------------------------------------
class MemoryAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a helpful voice AI assistant. "
                "You can remember past conversations and use them to give better answers. "
                "You respond concisely, clearly, and naturally without emojis or special formatting. "
                "You are friendly, curious, and slightly humorous."
            )
        )
        self._last_user_message = None
        self._last_assistant_message = None

    async def on_enter(self):
        """Called when agent enters the session."""
        await super().on_enter()
        # Optionally retrieve and inject initial context from Mem0
        try:
            logger.info("Retrieving initial context from Mem0")
            search_results = await mem0_client.search(
                "recent conversation context",
                filters={"AND": [{"user_id": MEM0_USER_ID}]},
                limit=3,
            )
            
            results = search_results.get("results", []) if isinstance(search_results, dict) else search_results
            memories = []
            
            for result in results:
                memory_text = result.get("memory") or result.get("text")
                if memory_text:
                    memories.append(memory_text)
            
            if memories:
                context = "Previous context: " + " | ".join(memories)
                logger.info(f"Initial memory context: {context}")
                # You could inject this into the initial prompt or instructions
                
        except Exception as e:
            logger.warning(f"Failed to retrieve initial context: {e}")

    async def on_user_turn_completed(
        self,
        turn_ctx: ChatContext,
        new_message: ChatMessage,
    ) -> None:
        """This is called after user completes their turn."""
        user_text = new_message.text_content
        
        if not user_text or len(user_text.strip()) < 5:
            return await super().on_user_turn_completed(turn_ctx, new_message)

        self._last_user_message = user_text
        logger.info(f"User said: {user_text}")

        # Store user message in Mem0
        try:
            logger.info(f"Storing user message in Mem0: {user_text}")
            await mem0_client.add(
                [{"role": "user", "content": user_text}],
                user_id=MEM0_USER_ID,
            )
        except Exception as e:
            logger.warning(f"Mem0 add failed: {e}")

        # Retrieve relevant memories
        try:
            search_results = await mem0_client.search(
                user_text,
                filters={"AND": [{"user_id": MEM0_USER_ID}]},
                limit=5,
            )

            memories = []
            results = search_results.get("results", []) if isinstance(search_results, dict) else search_results

            for result in results:
                memory_text = result.get("memory") or result.get("text")
                if memory_text:
                    memories.append(memory_text)

            if memories:
                memory_block = "\n\n".join(memories)
                logger.info(f"Injecting memory context:\n{memory_block}")

                # Inject memory as system context
                turn_ctx.add_message(
                    role="assistant",
                    content=(
                        "Relevant information from previous conversations:\n\n"
                        f"{memory_block}"
                    ),
                )
                await self.update_chat_ctx(turn_ctx)

        except Exception as e:
            logger.warning(f"Mem0 search failed: {e}")

        await super().on_user_turn_completed(turn_ctx, new_message)

    async def on_agent_turn_completed(
        self,
        turn_ctx: ChatContext,
    ) -> None:
        """Called after the agent completes its turn - this is where we capture the response."""
        
        # Get the last message from the assistant
        assistant_messages = [msg for msg in turn_ctx.messages if msg.role == "assistant"]
        
        if assistant_messages:
            last_response = assistant_messages[-1].text_content
            
            if last_response and last_response != self._last_assistant_message:
                self._last_assistant_message = last_response
                logger.info(f"Assistant said: {last_response}")
                
                # Store assistant response in Mem0
                try:
                    logger.info(f"Storing assistant response in Mem0: {last_response}")
                    await mem0_client.add(
                        [{"role": "assistant", "content": last_response}],
                        user_id=MEM0_USER_ID,
                    )
                except Exception as e:
                    logger.warning(f"Failed to store assistant response: {e}")
        
        await super().on_agent_turn_completed(turn_ctx)


# -------------------------------------------------
# Server + Prewarm
# -------------------------------------------------
server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


# -------------------------------------------------
# Agent Entrypoint
# -------------------------------------------------
@server.rtc_session()
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }
    
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model="gemini-2.5-flash-native-audio-preview-12-2025",
            proactivity=True,
            voice="Aoede",
            enable_affective_dialog=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    await session.start(
        agent=MemoryAssistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    await ctx.connect()


# -------------------------------------------------
# Run
# -------------------------------------------------
if __name__ == "__main__":
    cli.run_app(server)