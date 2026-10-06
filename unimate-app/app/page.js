"use client";

import { useEffect, useState } from "react";

const TOPIC_CATEGORIES = [

  {
    id: "registration",
    title: "Registration",
    questions: [
      "How do I register for the upcoming semester? ",
      "What are the registration deadlines?",
      "Can I register late or add/drop classes?"
    ],
  },

  {
    id: "club-info",
    title: "Club Info and Social Activities",
    questions: [
      "What student clubs are available to join? ",
      "How do I start a new club?",
      "Where can I check upcoming club events?"
    ],
  },

  {
    id: "withdrawal",
    title: "Withdrawal and Course Drop",
    questions: [
      "What is the policy for course withdrawal? ",
      "Will I get a tuition refund if I refund?",
      "Who do I contact to approve my withdrawal?"
    ],
  },

  {
    id: "navigation",
    title: "Navigation & Locations",
    questions: [
      "Where is the adminstration building? ",
      "When are the library opening hours?",
      "Which bldg is Mechanical floor located at?"
    ],
  },
];

export default function Home() {
  // 1. STATE: Array to store all messages in the current conversation
  const welcomeMessage = {
  id: "welcome",
  sender: "bot",
  text: "Hey! I'm Navi, your guide to AAU. Select a topic from the left sidebar or type your question below",
};

const [chatHistory, setChatHistory] = useState([]);
const [activeChatId, setActiveChatId] = useState(null);
const [searchQuery, setSearchQuery] = useState("");
const [historyLoaded, setHistoryLoaded] = useState(false);
const [inputValue, setInputValue] = useState("");
const [isSidebarOpen, setIsSidebarOpen] = useState(true);
const [expandedTopic, setExpandedTopic] = useState("registration");

useEffect(() => {
  const timer = setTimeout(() => {
    try {
      const saved = JSON.parse(localStorage.getItem("unimate-chats") || "[]");
      if (Array.isArray(saved)) setChatHistory(saved);
    } catch {
      // Start with empty history if saved data is invalid.
    }
    setHistoryLoaded(true);
  }, 0);

  return () => clearTimeout(timer);
}, []);

useEffect(() => {
  if (historyLoaded) {
    localStorage.setItem("unimate-chats", JSON.stringify(chatHistory));
  }
}, [chatHistory, historyLoaded]);

const activeChat = chatHistory.find((chat) => chat.id === activeChatId);
const messages = activeChat?.messages ?? [welcomeMessage];

const filteredHistory = chatHistory.filter((chat) =>
  chat.title.toLowerCase().includes(searchQuery.trim().toLowerCase())
);

  // 3. FUNCTION: Runs when user sends a message
  const sendMessageText = (textToSend) => {
  const question = textToSend.trim();
  if (!question) return;

  const chatId = activeChatId ?? crypto.randomUUID();
  const userMessage = {
    id: crypto.randomUUID(),
    sender: "user",
    text: question,
  };

  if (activeChatId) {
    setChatHistory((previous) =>
      previous.map((chat) =>
        chat.id === chatId
          ? {
              ...chat,
              messages: [...chat.messages, userMessage],
              updatedAt: Date.now(),
            }
          : chat
      )
    );
  } else {
    setChatHistory((previous) => [
      {
        id: chatId,
        title: question.slice(0, 50),
        updatedAt: Date.now(),
        messages: [welcomeMessage, userMessage],
      },
      ...previous,
    ]);
    setActiveChatId(chatId);
  }

  setInputValue("");

  // Your friend's RAG integration can replace this placeholder later.
  setTimeout(() => {
    const botMessage = {
      id: crypto.randomUUID(),
      sender: "bot",
      text: `You asked: "${question}". I am currently using dummy responses until we connect my trained AI model!`,
    };

    setChatHistory((previous) =>
      previous.map((chat) =>
        chat.id === chatId
          ? {
              ...chat,
              messages: [...chat.messages, botMessage],
              updatedAt: Date.now(),
            }
          : chat
      )
    );
  }, 1000);
};

  const handleSendMessage = (e) => {
    e.preventDefault(); // Prevents page reload on form submit
    sendMessageText(inputValue);
  }; // Don't send empty messages

  return (

    <div className="flex h-screen bg-slate-900 text-slate-100 overflow-hidden">
      <aside className={`${isSidebarOpen ? "w-80" : "w-0"} transition-all duration-300 ease-in-out bg-slate-950 border-r border-slate-800 flex flex-col overflow-hidden shrink-0`}
      >
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="font-bold text-sm tracking-wide text-slate-200">
            Explore Topics
          </h2>
          <span className="text-xs text-slate-500">
            Guide
          </span>
        </div>


        <div className="p-3 border-b border-slate-800">
          <button
            type="button"
            onClick={() => {
              setActiveChatId(null);
              setInputValue("");
            }}
            className="mb-3 w-full rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-500"
          >
            + New chat
          </button>

          {/* Search Input Box */}
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search past chats..."
            className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />

          {/* Filtered History List */}
          <div className="mt-3 space-y-1">
            <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider px-1">
              Recent Chats
            </p>
            {filteredHistory.length > 0 ? (
              filteredHistory.map((chat) => (   
                <button
                  key={chat.id}
                  onClick={() => setActiveChatId(chat.id)}
                  className="w-full text-left px-2 py-1.5 rounded-md hover:bg-slate-900 text-xs text-slate-400 hover:text-slate-200 transition-colors flex justify-between items-center"
                >
                  <span className="truncate">{chat.title}</span>
                  <span className="text-[10px] text-slate-600 shrink-0 ml-2">
                    {new Date(chat.updatedAt).toLocaleDateString()}
                  </span>
                </button>
              ))
            ) : (
              <p className="text-xs text-slate-600 p-1">No chats found</p>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {TOPIC_CATEGORIES.map((category) => {
            const isOpen = expandedTopic === category.id;

            return (
              <div
                key={category.id}
                className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/50">
                <button
                  onClick={() => setExpandedTopic(isOpen ? null : category.id)}
                  className="w-full text-left p-3 flex justify-between items-center text-sm font-medium hover:bg-slate-800/60 transition-colors"
                >
                  <span>{category.title}</span>
                  <span className="text-slate-500 text-xs">
                    {isOpen ? "▲" : "▼"}
                  </span>
                </button>

                {isOpen && (
                  <div className="p-2 pt-0 space-y-1 bg-slate-950/40 border-t border-slate-800/50">
                    {category.questions.map((q, idx) => (
                      <button key={idx}
                        onClick={() => sendMessageText(q)}
                        className="w-full text-left p-2 rounded-lg text-xs text-slate-300 hover:text-white hover:bg-blue-600/20 hover:border-blue-500/40 border border-transparent transition-all">
                        .{q}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </aside>


      <div className="flex-1 flex flex-col h-full overflow-hidden">

        {/* HEADER */}
        <header className="p-4 border-b border-slate-800 bg-slate-950 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setIsSidebarOpen((open) => !open)}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition-colors"
            >
              {isSidebarOpen ? "◀ Hide Topics" : "▶ Show Topics"}
            </button>
            <h1 className="font-bold text-base text-slate-100">
              UniMate
            </h1>
          </div>
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
    </div>
  );
}