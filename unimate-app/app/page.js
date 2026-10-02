"use client";

import { useState } from "react";



export default function Home() {
  // 1. STATE: Array to store all messages in the current conversation
  const [ messages, setMessages ] = useState([
    { id: 1, sender: "bot", text: "Hey! I'm Navi, your guide to AAU. How can I help you today?" },
  ]);

  // 2. STATE: Text currently inside the input box
  const [ inputValue, setInputValue ] = useState("");

  // 3. FUNCTION: Runs when user sends a message
  const handleSendMessage = (e) => {
    e.preventDefault(); // Prevents page reload on form submit
    if (!inputValue.trim()) return; // Don't send empty messages

    // Create user message object
    const userMessage = {
      id: Date.now(),
      sender: "user",
      text: inputValue,
    };

    // Update messages state (adds user message to existing array)
    setMessages((prev) => [ ...prev, userMessage ]);

    // Clear input box
    const currentInput = inputValue;
    setInputValue("");

    // Simulate AI response after a short delay (Placeholder for backend API integration)
    setTimeout(() => {
      const botMessage = {
        id: Date.now() + 1,
        sender: "bot",
        text: `You asked: "${currentInput}". I am currently using dummy responses until we connect my trained AI model!`,
      };
      setMessages((prev) => [ ...prev, botMessage ]);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-screen bg-slate-900 text-slate-100">

      {/* HEADER */}
      <header className="p-4 border-b border-slate-800 bg-slate-950 font-bold text-lg text-center">
        UniMate
      </header>

      {/* CHAT MESSAGES CONTAINER */}
      <main className="flex-1 overflow-y-auto p-4 space-y-4 max-w-3xl w-full mx-auto">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm shadow-md ${msg.sender === "user"
                ? "bg-blue-600 text-white rounded-br-none"
                : "bg-slate-800 text-slate-200 border border-slate-700 rounded-bl-none"
                }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </main>

      {/* INPUT FORM */}
      <footer className="p-4 border-t border-slate-800 bg-slate-950">
        <form onSubmit={handleSendMessage} className="max-w-3xl mx-auto flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask anything about AAU..."
            className="flex-1 bg-slate-800 border border-slate-700 text-slate-100 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500 placeholder-slate-400"
          />
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-6 py-3 rounded-xl text-sm transition-colors"
          >
            Ask
          </button>
        </form>
      </footer>

    </div>
  );
}