import logging
from dotenv import load_dotenv

from mem0 import AsyncMemoryClient

from livekit.agents import (
    JobContext,
    JobProcess,
    Agent,
    AgentSession,
    AgentServer,
    cli,
    ChatContext,
    ChatMessage,
    room_io,
)
from livekit.plugins import silero, google

# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------

load_dotenv(".env.local")

logger = logging.getLogger("gemini-realtime-mem0")
logger.setLevel(logging.INFO)

server = AgentServer()

# Mem0
RAG_USER_ID = "livekit-gemini-realtime"
mem0_client = AsyncMemoryClient()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm

# -----------------------------------------------------------------------------
# Memory-Enabled Gemini Agent
# -----------------------------------------------------------------------------

class MemoryEnabledGeminiAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""
            You are a helpful voice AI assistant that can see the world around you.
            You have long-term memory and should use relevant past context
            naturally and silently to improve your responses.
            """
        )

    # 🔑 THIS IS THE CORRECT HOOK FOR GEMINI REALTIME
    async def on_transcription_completed(
        self,
        chat_ctx: ChatContext,
        message: ChatMessage,
    ) -> None:
        user_text = message.text_content
        if not user_text:
            return

        logger.info(f"📝 Final transcription: {user_text}")

        # ------------------------------------------------------------------
        # 1. Store user message in Mem0
        # ------------------------------------------------------------------
        try:
            logger.info("[Mem0] Saving user message")
            await mem0_client.add(
                [{"role": "user", "content": user_text}],
                user_id=RAG_USER_ID,
            )
        except Exception as e:
            logger.warning(f"[Mem0] Add failed: {e}")

        # ------------------------------------------------------------------
        # 2. Retrieve relevant memories
        # ------------------------------------------------------------------
        try:
            logger.info("[Mem0] Searching memories")
            results = await mem0_client.search(
                user_text,
                user_id=RAG_USER_ID,
            )

            memories = results.get("results", []) if results else []
            if not memories:
                logger.info("[Mem0] No relevant memories")
                return

            context_lines = []
            for m in memories:
                text = m.get("memory") or m.get("text")
                if text:
                    context_lines.append(f"- {text}")

            rag_context = (
                "Relevant past context:\n"
                + "\n".join(context_lines)
            )

            logger.info(f"[Mem0] Injecting SYSTEM context:\n{rag_context}")

            # 🔑 SYSTEM MESSAGE — NOT assistant
            chat_ctx.add_message(
                role="system",
                content=rag_context,
            )

            await self.update_chat_ctx(chat_ctx)

        except Exception as e:
            logger.warning(f"[Mem0] Search failed: {e}")


# -----------------------------------------------------------------------------
# RTC Entrypoint
# -----------------------------------------------------------------------------

@server.rtc_session()
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model="gemini-2.5-flash-native-audio-preview-12-2025",
            proactivity=True,
            voice="Aoede",
            enable_affective_dialog=True,
        ),
        vad=ctx.proc.userdata["vad"],
    )

    await session.start(
        room=ctx.room,
        agent=MemoryEnabledGeminiAgent(),
        room_options=room_io.RoomOptions(
            video_input=True,
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions="Greet the user warmly and offer help."
    )


# -----------------------------------------------------------------------------
# Run
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    cli.run_app(server)
