from core.chat_engine import ask_question

# 👉 CHANGE THESE
pdf_id = "e6cb5c39-7f94-4d28-a32d-4137b71baeaf"
device_id = "test_device_123"
chat_id = "chat_manual_1"

print("\n💬 RAG CHAT TEST MODE STARTED")
print("Type 'exit' to stop\n")

while True:
    question = input("You: ")

    if question.lower() == "exit":
        print("👋 Chat ended")
        break

    try:
        answer = ask_question(question, pdf_id, device_id, chat_id)

        print("\n🤖 AI:", answer)
        print("\n" + "-"*50 + "\n")

    except Exception as e:
        print("❌ Error:", e)