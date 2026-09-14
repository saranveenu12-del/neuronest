import { FormEvent, useMemo, useState } from "react";
import { BookOpen, CheckCircle2, Leaf, Loader2, Send, ShieldCheck, Sparkles } from "lucide-react";
import { Streamdown } from "streamdown";
import { trpc } from "@/lib/trpc";
import { NATURE_ENTRIES, NATURE_QUESTION_COUNT } from "@shared/natureKnowledge";

type Message = {
  id: number;
  role: "assistant" | "user";
  text: string;
  source?: string;
  confidence?: number | null;
  matchedQuestion?: string | null;
};

const starterPrompts = [
  "What is biodiversity?",
  "Help me understand a difficult idea",
  "What should I learn about today?",
  "How do I build a good learning habit?",
];

export default function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: "assistant",
      text: "Hello. I’m NeuroNest, your evolving AI companion for learning, reflection, and discovery. Nature is one of my learning domains, but you can bring me any thoughtful question.",
      source: "welcome",
    },
  ]);
  const ask = trpc.chat.ask.useMutation();
  const explorerQuestions = useMemo(() => NATURE_ENTRIES.slice(0, 12), []);

  const submit = async (event?: FormEvent) => {
    event?.preventDefault();
    const message = input.trim();
    if (!message || ask.isPending) return;
    const id = Date.now();
    setMessages(previous => [...previous, { id, role: "user", text: message }]);
    setInput("");
    try {
      const result = await ask.mutateAsync({ message });
      setMessages(previous => [
        ...previous,
        {
          id: id + 1,
          role: "assistant",
          text: result.response,
          source: result.source,
          confidence: result.confidence,
          matchedQuestion: result.matchedQuestion,
        },
      ]);
    } catch {
      setMessages(previous => [
        ...previous,
        {
          id: id + 1,
          role: "assistant",
          text: "I couldn’t process that message. Please try again.",
          source: "error",
        },
      ]);
    }
  };

  return (
    <main className="site-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="NeuroNest home">
          <span className="brand-mark"><Leaf size={20} strokeWidth={2.5} /></span>
          <span>NeuroNest</span>
        </a>
        <div className="topbar-note"><span className="live-dot" /> Learn · remember · grow</div>
      </header>

      <section className="hero-grid">
        <div className="hero-copy">
          <p className="eyebrow"><Sparkles size={15} /> A calmer way to get curious</p>
          <h1>Meet a companion for <em>curious minds.</em></h1>
          <p className="hero-lede">NeuroNest helps you explore ideas, learn clearly, remember what matters, and grow through conversation—with a carefully reviewed nature library as one of its learning foundations.</p>
          <div className="hero-proof">
            <span><CheckCircle2 size={17} /> {NATURE_QUESTION_COUNT} reviewed questions</span>
            <span><ShieldCheck size={17} /> Uncertainty is stated clearly</span>
          </div>
        </div>
        <div className="orbital-art" aria-hidden="true">
          <div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="orbit orbit-three" />
          <div className="glow-orb"><Leaf size={54} strokeWidth={1.2} /></div>
          <span className="orbit-dot dot-one" /><span className="orbit-dot dot-two" /><span className="orbit-dot dot-three" />
        </div>
      </section>

      <section className="workspace-grid" aria-label="NeuroNest workspace">
        <div className="chat-card panel">
          <div className="panel-heading">
            <div><p className="section-kicker">Conversation</p><h2>Talk to NeuroNest</h2></div>
            <span className="status-pill"><span className="live-dot" /> Online</span>
          </div>
          <div className="message-list" aria-live="polite">
            {messages.map(message => (
              <div className={`message-row ${message.role}`} key={message.id}>
                {message.role === "assistant" && <div className="avatar"><Leaf size={16} /></div>}
                <div className="message-stack">
                  <div className="message-bubble"><Streamdown>{message.text}</Streamdown></div>
                  {message.role === "assistant" && message.source !== "welcome" && (
                    <div className="message-meta">
                      <span>{message.source === "curated_nature_knowledge" ? "Reviewed knowledge" : message.source === "hosted_llm" ? "Thoughtful model answer" : "Safe fallback"}</span>
                      {message.confidence !== null && message.confidence !== undefined && <span>Match {Math.round(message.confidence * 100)}%</span>}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {ask.isPending && <div className="message-row assistant"><div className="avatar"><Leaf size={16} /></div><div className="message-bubble typing"><Loader2 size={16} className="spin" /> Thinking carefully…</div></div>}
          </div>
          <form className="composer" onSubmit={submit}>
            <label className="sr-only" htmlFor="question">Ask a nature question</label>
            <input id="question" value={input} onChange={event => setInput(event.target.value)} placeholder="Ask about plants, animals, weather…" maxLength={500} />
            <button type="submit" aria-label="Send question" disabled={!input.trim() || ask.isPending}><Send size={18} /></button>
          </form>
          <div className="starter-row" aria-label="Suggested questions">
            {starterPrompts.map(prompt => <button key={prompt} type="button" onClick={() => setInput(prompt)}>{prompt}</button>)}
          </div>
        </div>

        <aside className="explorer-card panel">
          <div className="panel-heading compact"><div><p className="section-kicker">Learning library</p><h2>Explore a starting point</h2></div><BookOpen size={20} /></div>
          <p className="explorer-intro">Nature is a major NeuroNest learning domain. Browse reviewed prompts here, or use the chat for any subject.</p>
          <div className="explorer-list">
            {explorerQuestions.map(entry => <button key={entry.question} type="button" onClick={() => setInput(entry.question)}><span>{entry.question}</span><span className="arrow">↗</span></button>)}
          </div>
          <div className="library-note"><ShieldCheck size={17} /><span>Known questions are answered from the reviewed library before any model fallback.</span></div>
        </aside>
      </section>

      <footer className="footer"><span>NeuroNest Nature Learning</span><span>Learn carefully. Stay curious.</span></footer>
    </main>
  );
}
