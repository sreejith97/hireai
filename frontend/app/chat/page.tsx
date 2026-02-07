
"use client";
import { useState, useRef, useEffect } from "react";
import { Send, User, Sparkles, MoreVertical } from "lucide-react";
import axios from "axios";

interface Message {
    id: string;
    sender: "user" | "bot";
    text: string;
    timestamp: Date;
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "welcome",
            sender: "bot",
            text: "Hello. I am your HR Assistant. Please enter your Employee ID (e.g., EMP001) to begin.",
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState("");
    const [employeeId, setEmployeeId] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            sender: "user",
            text: input,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setIsLoading(true);

        try {
            const response = await axios.post("http://localhost:8000/chat", {
                message: userMsg.text,
                employee_id: employeeId
            });

            if (response.data.verified_employee_id) {
                setEmployeeId(response.data.verified_employee_id);
            }

            const botMsg: Message = {
                id: (Date.now() + 1).toString(),
                sender: "bot",
                text: response.data.response || "I am unable to process that request.",
                timestamp: new Date()
            };

            setMessages(prev => [...prev, botMsg]);
        } catch (error) {
            setMessages(prev => [...prev, {
                id: (Date.now() + 1).toString(),
                sender: "bot",
                text: "System unavailable. Please try again later.",
                timestamp: new Date()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-slate-50 items-center justify-center p-0 md:p-6 font-sans">
            <div className="w-full max-w-4xl bg-white md:rounded-2xl shadow-xl border border-slate-200 overflow-hidden flex flex-col h-full md:h-[85vh]">

                {/* Header */}
                <div className="bg-white border-b border-slate-100 p-5 flex items-center justify-between sticky top-0 z-10">
                    <div className="flex items-center gap-3">
                        <div className="bg-blue-600 p-2 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
                            <Sparkles className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h1 className="text-lg font-semibold text-slate-800 tracking-tight">HR Assistant</h1>
                            <p className="text-slate-500 text-xs font-medium">Automated Support</p>
                        </div>
                    </div>
                    <button className="text-slate-400 hover:text-slate-600 transition-colors p-2 rounded-full hover:bg-slate-50">
                        <MoreVertical className="w-5 h-5" />
                    </button>
                </div>

                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-8 bg-white scroll-smooth">
                    {messages.map((msg) => (
                        <div key={msg.id} className={`flex w-full ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
                            <div className={`flex max-w-[85%] md:max-w-[70%] gap-4 ${msg.sender === "user" ? "flex-row-reverse" : "flex-row"}`}>

                                {/* Avatar */}
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm ${msg.sender === "user" ? "bg-slate-800" : "bg-blue-600"
                                    }`}>
                                    {msg.sender === "user" ?
                                        <User className="w-4 h-4 text-white" /> :
                                        <Sparkles className="w-4 h-4 text-white" />
                                    }
                                </div>

                                {/* Bubble */}
                                <div className={`px-5 py-3.5 rounded-2xl shadow-sm text-sm leading-6 ${msg.sender === "user"
                                        ? "bg-slate-800 text-white rounded-tr-none"
                                        : "bg-slate-50 text-slate-700 border border-slate-100 rounded-tl-none"
                                    }`}>
                                    <p className="whitespace-pre-wrap">{msg.text}</p>
                                    <p className={`text-[10px] mt-2 block opacity-60 ${msg.sender === 'user' ? 'text-slate-300' : 'text-slate-400'}`}>
                                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex justify-start pl-12">
                            <div className="bg-slate-50 border border-slate-100 rounded-2xl rounded-tl-none p-4 shadow-sm">
                                <div className="flex space-x-2 items-center h-4">
                                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></div>
                                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0.15s" }}></div>
                                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0.3s" }}></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-5 bg-white border-t border-slate-100">
                    <div className="relative flex items-center">
                        <input
                            type="text"
                            placeholder="Type a message..."
                            className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-sm rounded-xl pl-5 pr-14 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all placeholder:text-slate-400"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && handleSend()}
                            disabled={isLoading}
                        />
                        <button
                            onClick={handleSend}
                            disabled={isLoading || !input.trim()}
                            className="absolute right-2 p-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 transition-all shadow-sm"
                        >
                            <Send className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
