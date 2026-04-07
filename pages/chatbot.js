import { useState, useEffect, useRef } from "react";
import { Send } from "lucide-react";

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { sender: "bot", raw: "Hello 👋\nAsk about your finance dashboard." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // ✅ Clean ChatGPT style text
  const formatResponse = (text) => {
    if (!text) return "";

    return text
      .split("\n")
      .filter((line) => line.trim() !== "")
      .map((line, i) => (
        <div key={i} className="mb-1">{line}</div>
      ));
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:5000/api/chatbot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ message: input }),
      });

      const data = await res.json();

      const botMsg = {
        sender: "bot",
        raw: data.reply,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", raw: "Error connecting to AI." },
      ]);
    }

    setLoading(false);
    setInput("");
  };

  return (
    <div className="flex flex-col h-screen bg-[#343541] text-white font-[Inter]">

      {/* HEADER */}
      <div className="p-4 border-b border-gray-700 text-center text-lg font-semibold">
        Finance AI Assistant
      </div>

      {/* CHAT AREA */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">

          {messages.map((m, i) => (
            <div key={i} className="flex gap-4">

              {/* Avatar */}
              <div className={`w-8 h-8 flex items-center justify-center rounded-full text-sm font-bold ${
                m.sender === "user"
                  ? "bg-blue-600"
                  : "bg-gray-600"
              }`}>
                {m.sender === "user" ? "U" : "AI"}
              </div>

              {/* Message */}
              <div className="text-sm leading-relaxed">
                {m.sender === "bot"
                  ? formatResponse(m.raw)
                  : m.text}
              </div>

            </div>
          ))}

          {loading && (
            <div className="text-gray-400 text-sm animate-pulse">
              Thinking...
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* INPUT */}
      <div className="border-t border-gray-700 bg-[#40414f] p-4">
        <div className="max-w-3xl mx-auto flex items-center bg-[#343541] rounded-xl px-3 py-2">

          <input
            type="text"
            className="flex-1 bg-transparent outline-none text-sm px-2"
            placeholder="Ask about your finance app..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />

          <button
            onClick={sendMessage}
            className="bg-green-500 p-2 rounded-lg hover:opacity-80"
          >
            <Send size={16} />
          </button>

        </div>
      </div>
    </div>
  );
}