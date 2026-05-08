import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

type Message = {
  role: string;
  content: string;
};

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem("chatHistory");
    if (saved) {
      setMessages(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("chatHistory", JSON.stringify(messages));
  }, [messages]);

  const uploadFile = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    await axios.post("http://127.0.0.1:8000/upload", formData);

    alert("Document uploaded successfully");
  };

  const askQuestion = async () => {
    if (!question) return;

    const userMessage = {
      role: "user",
      content: question,
    };

    setMessages((prev) => [...prev, userMessage]);

    const response = await axios.post(
      "http://127.0.0.1:8000/ask",
      {
        question: question,
      }
    );

    const botMessage = {
      role: "assistant",
      content: response.data.answer,
    };

    setMessages((prev) => [...prev, botMessage]);

    setQuestion("");
  };

  const clearChat = () => {
    setMessages([]);
    localStorage.removeItem("chatHistory");
  };

  return (
    <div className="container">
      <h1>AI20 Document Q&A</h1>

      <div className="upload-section">
        <input
          type="file"
          onChange={(e) =>
            setFile(e.target.files ? e.target.files[0] : null)
          }
        />

        <button onClick={uploadFile}>Upload Document</button>
      </div>

      <div className="chat-section">
        <div className="messages">
          {messages.map((msg, index) => (
            <div key={index} className={msg.role}>
              <strong>{msg.role}:</strong> {msg.content}
            </div>
          ))}
        </div>

        <input
          type="text"
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />

        <div className="buttons">
          <button onClick={askQuestion}>Ask</button>
          <button onClick={clearChat}>Clear Chat</button>
        </div>
      </div>
    </div>
  );
}

export default App;