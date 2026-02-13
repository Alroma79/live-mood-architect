import { FormEvent, useMemo, useState } from "react";

type ApiSuccess = {
  affirmation: string;
};

type ApiError = {
  error?: string;
};

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const apiBaseUrl = useMemo(() => {
    const configured = import.meta.env.VITE_API_BASE_URL?.trim();
    return configured || DEFAULT_API_BASE_URL;
  }, []);

  const [name, setName] = useState("");
  const [feeling, setFeeling] = useState("");
  const [affirmation, setAffirmation] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setAffirmation("");

    if (!name.trim() || !feeling.trim()) {
      setError("Please enter both your name and how you feel.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${apiBaseUrl}/api/affirmation`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: name.trim(), feeling: feeling.trim() }),
      });

      const payload = (await response.json().catch(() => ({}))) as ApiSuccess | ApiError;

      if (response.ok) {
        const message = (payload as ApiSuccess).affirmation?.trim();
        setAffirmation(message || "Your affirmation is ready.");
        return;
      }

      if (response.status === 400) {
        setError(payload.error || "Please check your input and try again.");
        return;
      }

      if (response.status === 502 || response.status === 504) {
        setError("The affirmation service is temporarily unavailable. Please try again shortly.");
        return;
      }

      setError("Something went wrong while generating your affirmation. Please try again.");
    } catch {
      setError("We could not reach the server. Please check your connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page">
      <section className="card">
        <h1>Live Mood Architect</h1>
        <p className="subtitle">Share how you feel and receive a short, supportive affirmation.</p>

        <form onSubmit={handleSubmit} className="form" noValidate>
          <label htmlFor="name">Name</label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(event) => {
              setName(event.target.value);
              setAffirmation("");
              setError("");
            }}
            placeholder="Your name"
            disabled={loading}
          />

          <label htmlFor="feeling">How are you feeling?</label>
          <textarea
            id="feeling"
            value={feeling}
            onChange={(event) => {
              setFeeling(event.target.value);
              setAffirmation("");
              setError("");
            }}
            placeholder="Tell us a little about what you are feeling right now"
            rows={5}
            disabled={loading}
          />

          <button type="submit" disabled={loading}>
            {loading ? "Generating..." : "Generate affirmation"}
          </button>
        </form>

        {error ? (
          <div className="status error" role="alert">
            {error}
          </div>
        ) : null}

        {affirmation ? (
          <div className="status result" aria-live="polite">
            {affirmation}
          </div>
        ) : null}
      </section>
    </main>
  );
}

export default App;
