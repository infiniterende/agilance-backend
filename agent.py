from __future__ import annotations
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
from dotenv import load_dotenv
from api import AssistantFnc
from prompts import WELCOME_MESSAGE, INSTRUCTIONS
import os
from models import ChatSession, Message
from livekit.plugins import openai
import asyncio

from db import SessionLocal

db = SessionLocal()


async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()

    model = openai.realtime.RealtimeModel(
        instructions=INSTRUCTIONS,
        voice="shimmer",
        temperature=0.8,
        modalities=["audio", "text"],
    )
    assistant_fnc = AssistantFnc()
    assistant = MultimodalAgent(model=model, fnc_ctx=assistant_fnc)
    assistant.start(ctx.room)

    session = model.sessions[0]
    session.conversation.item.create(
        llm.ChatMessage(role="assistant", content=WELCOME_MESSAGE)
    )
    session.response.create()

    @session.on("user_speech_committed")
    def on_user_speech_committed(msg: llm.ChatMessage):
        # Convert content list to string if needed
        if isinstance(msg.content, list):
            msg.content = "\n".join(
                "[image]" if isinstance(x, llm.ChatImage) else x for x in msg
            )

        asyncio.create_task(handle_user_message(msg))

        # Use context manager for DB session

        async def handle_user_message(msg: llm.ChatMessage):
            db = SessionLocal()
            existing_sessions = db.query(ChatSession).count()
            session_id = f"session_{existing_sessions + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Retrieve or create ChatSession
            chat_session = (
                db.query(ChatSession)
                .filter(ChatSession.session_id == session_id)
                .first()
            )
            if not chat_session:
                chat_session = ChatSession(
                    session_id=session_id,
                    current_question=0,
                    responses={},
                    risk_score=0,
                    assessment_complete=False,
                    messages=[],
                    conversation_history=[],
                )

            # Create messages
            user_msg = Message(session_id=session_id, role="user", content=msg.content)
            welcome_msg = Message(
                session_id=session_id, role="assistant", content=WELCOME_MESSAGE
            )

            # Append messages to session
            chat_session.messages.extend([user_msg, welcome_msg])
            chat_session.conversation_history.extend([user_msg, welcome_msg])
            chat_session.current_question += 1

            # Save session
            db.add(chat_session)
            db.commit()
            db.refresh(chat_session)

            # If assessment is complete, extract patient data and save
            if (
                chat_session.current_question >= 10
                and not chat_session.assessment_complete
            ):
                chat_session.assessment_complete = True
                db.add(chat_session)
                db.commit()

                # Extract patient data via LLM
                conversation_history = [
                    m.content for m in chat_session.conversation_history
                ]
                patient_data = await assistant_fnc.extract_patient_data(
                    conversation_history
                )

                print(patient_data)

                # Create patient in DB
                await assistant_fnc.create_patient(**patient_data)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
