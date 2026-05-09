import { useEffect, useState } from "react";
import "./App.css";

interface Message {
  role: string;
  content: string;
}

interface ChatSession {
  id: number;
  title: string;
  messages: Message[];
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState(0);

  const API_URL = "https://ai20-doc-qa.onrender.com";

  useEffect(() => {
    const saved = localStorage.getItem("chat_sessions");

    if (saved) {
      const parsed = JSON.parse(saved);
      setSessions(parsed);

      if (parsed.length > 0) {
        setMessages(parsed[0].messages);
      }
    }
  }, []);

  const saveSession = (updatedMessages: Message[]) => {
    const updatedSessions = [...sessions];

    updatedSessions[currentSession] = {
      id: currentSession,
      title: `Chat ${currentSession + 1}`,
      messages: updatedMessages,
    };

    setSessions(updatedSessions);
    localStorage.setItem("chat_sessions", JSON.stringify(updatedSessions));
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      alert(data.message);
    } catch (error) {
      alert("Upload failed. Please try again.");
      console.log(error);
    }
  };

  const askQuestion = async () => {
    if (!question) return;

    const userMessage: Message = {
      role: "user",
      content: question,
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
        }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        role: "assistant",
        content: data.answer,
      };

      const finalMessages = [...updatedMessages, assistantMessage];

      setMessages(finalMessages);
      saveSession(finalMessages);
    } catch (error) {
      const errorMessage: Message = {
        role: "assistant",
        content: "Something went wrong. Please try again.",
      };

      setMessages([...updatedMessages, errorMessage]);
      console.log(error);
    }

    setQuestion("");
  };

  const clearChat = () => {
    setMessages([]);

    const updatedSessions = [...sessions];

    updatedSessions[currentSession] = {
      id: currentSession,
      title: `Chat ${currentSession + 1}`,
      messages: [],
    };

    setSessions(updatedSessions);
    localStorage.setItem("chat_sessions", JSON.stringify(updatedSessions));
  };

  const newChat = () => {
    const newSessionId = sessions.length;

    const newSession: ChatSession = {
      id: newSessionId,
      title: `Chat ${newSessionId + 1}`,
      messages: [],
    };

    const updatedSessions = [...sessions, newSession];

    setSessions(updatedSessions);
    localStorage.setItem("chat_sessions", JSON.stringify(updatedSessions));
    setCurrentSession(newSessionId);
    setMessages([]);
  };

  const loadChat = (index: number) => {
    setCurrentSession(index);
    setMessages(sessions[index].messages);
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <h2>Chat History</h2>

        <button onClick={newChat}>New Chat</button>

        {sessions.map((session, index) => (
          <div
            key={index}
            className="chat-item"
            onClick={() => loadChat(index)}
          >
            {session.title}
          </div>
        ))}
      </div>

      <div className="main-content">
        <h1>AI20 Document Q&A</h1>

        <input
          type="file"
          accept=".pdf,.txt"
          onChange={(e) => {
            if (e.target.files) {
              setFile(e.target.files[0]);
            }
          }}
        />

        <button onClick={handleUpload}>Upload</button>

        <div className="chat-box">
          {messages.map((msg, index) => (
            <div key={index} className={msg.role}>
              <b>{msg.role}:</b> {msg.content}
            </div>
          ))}
        </div>

        <input
          type="text"
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />

        <button onClick={askQuestion}>Ask</button>
        <button onClick={clearChat}>Clear Chat</button>
      </div>
    </div>
  );
}

export default App;