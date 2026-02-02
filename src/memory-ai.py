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
)

from livekit.plugins import (
    silero,
    noise_cancellation,
)

from livekit.plugins.turn_detector.multilingual import MultilingualModel

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

# Stable user ID for memory (you can later swap this for participant identity)
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

    async def on_user_turn_completed(
        self,
        turn_ctx: ChatContext,
        new_message: ChatMessage,
    ) -> None:
        user_text = new_message.text_content
        if not user_text:
            return await super().on_user_turn_completed(turn_ctx, new_message)
        
        if len(user_text.strip()) < 5:
            await super().on_user_turn_completed(turn_ctx, new_message)
            return

        # -----------------------------
        # 1. Store user message in Mem0
        # -----------------------------
        try:
            logger.info(f"Storing message in Mem0: {user_text}")
            await mem0_client.add(
                [{"role": "user", "content": user_text}],
                user_id=MEM0_USER_ID,
            )
        except Exception as e:
            logger.warning(f"Mem0 add failed: {e}")

        # -----------------------------
        # 2. Retrieve relevant memories
        # -----------------------------
        try:
            # Use the named 'query' argument
            search_results = await mem0_client.search(
                user_text,
                filters={"AND": [{"user_id": MEM0_USER_ID}]},
            )

            # Note: Mem0 V2 sometimes returns a list directly or a dict with a 'results' key.
            # The official example you provided expects a dict.
            memories = []
            
            # Adding a safety check for the structure
            results = search_results.get("results", []) if isinstance(search_results, dict) else search_results

            for result in results:
                memory_text = result.get("memory") or result.get("text")
                if memory_text:
                    memories.append(memory_text)

            if memories:
                memory_block = "\n\n".join(memories)
                logger.info(f"Injecting memory context:\n{memory_block}")

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
        stt=inference.STT(
            model="assemblyai/universal-streaming",
            language="en",
        ),
        llm=inference.LLM(
            model="openai/gpt-4.1-mini",
        ),
        tts=inference.TTS(
            model="cartesia/sonic-3",
            voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
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
