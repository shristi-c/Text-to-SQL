/* eslint-disable no-unused-vars */
import { useState } from "react";

const domains = {
  it: {
    name: "IT Intelligence",
    shortName: "IT",
    subtitle: "Support & Ticket Analytics",
    description:
      "Explore customer support tickets, queues, priorities, languages and tags using natural language.",
    accent: "it",
    metrics: [
      { label: "Total Tickets", value: "44,339" },
      { label: "Total Tags", value: "225,093" },
      { label: "Data Sources", value: "3" },
      { label: "Tables", value: "2" },
    ],
    examples: [
      "How many IT tickets are there?",
      "What are the most common ticket types?",
      "Which queues have the most tickets?",
      "How many tickets have no answer?",
    ],
  },

  retail: {
    name: "Retail Intelligence",
    shortName: "Retail",
    subtitle: "Sales & Supply Chain Analytics",
    description:
      "Understand customers, orders, products, sales and profitability through natural language.",
    accent: "retail",
    metrics: [
      { label: "Customers", value: "793" },
      { label: "Orders", value: "5,009" },
      { label: "Products", value: "1,894" },
      { label: "Order Items", value: "9,994" },
    ],
    examples: [
      "What are the top 10 products by sales?",
      "Which category has the highest profit?",
      "What is the total sales amount?",
      "Which region has the highest sales?",
    ],
  },

  airline: {
    name: "Airline Intelligence",
    shortName: "Airline",
    subtitle: "Flight & Travel Analytics",
    description:
      "Query flights, airports, bookings, passengers, aircraft and fares using natural language.",
    accent: "airline",
    metrics: [
      { label: "Flights", value: "33,121" },
      { label: "Airports", value: "104" },
      { label: "Bookings", value: "262,788" },
      { label: "Passengers", value: "366,733" },
    ],
    examples: [
      "How many flights are there?",
      "Which airports have the most departures?",
      "How many flights are cancelled?",
      "Which aircraft is used most often?",
    ],
  },
};

function App() {
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sql, setSql] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const domain = selectedDomain ? domains[selectedDomain] : null;

  const selectDomain = (domainKey) => {
    setSelectedDomain(domainKey);
    setQuestion("");
    setAnswer("");
    setSql("");
    setData(null);
    setError("");
  };

  const goHome = () => {
    setSelectedDomain(null);
    setQuestion("");
    setAnswer("");
    setSql("");
    setData(null);
    setError("");
  };

  const selectExample = (example) => {
    setQuestion(example);
    setAnswer("");
    setSql("");
    setData(null);
    setError("");
  };

  const clearAll = () => {
    setQuestion("");
    setAnswer("");
    setSql("");
    setData(null);
    setError("");
  };

  const askQuestion = async () => {
    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setLoading(true);
    setAnswer("");
    setSql("");
    setData(null);
    setError("");

    try {
     const response = await fetch(
  "http://127.0.0.1:8000/query?question=" +
    encodeURIComponent(question) +
    "&domain=" +
    encodeURIComponent(selectedDomain),
  {
    method: "POST",
  }
);

      const result = await response.json();

      if (!result.success) {
        setError(result.error || "Something went wrong.");
        setSql(result.sql || "");
        return;
      }

      setAnswer(result.answer || "");
      setSql(result.sql || "");
      setData(result.data || null);
    } catch (err) {
      setError(
        "Could not connect to the backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  if (!selectedDomain) {
    return (
      <div className="app">
        <nav className="navbar">
          <button className="brand-button" onClick={goHome}>
            T2<span>SQL</span>
          </button>

          <div className="nav-links">
            <a href="#domains">Domains</a>
            <a href="#how-it-works">How it works</a>
          </div>

          <div className="nav-status">
            <span className="status-dot"></span>
            Database Connected
          </div>
        </nav>

        <main>
          <section className="hero">
            <div className="hero-grid"></div>

            <div className="hero-content">
              <p className="eyebrow">NATURAL LANGUAGE DATABASE INTELLIGENCE</p>

              <h1>
                Ask your data.
                <br />
                <em>Understand the answer.</em>
              </h1>

              <p className="hero-description">
                Transform everyday questions into SQL queries and meaningful
                database insights — without writing SQL yourself.
              </p>

              <a href="#domains" className="hero-button">
                Explore Domains <span>→</span>
              </a>
            </div>

            <div className="hero-mark">
              <span>01</span>
              <div></div>
              <span>03</span>
            </div>
          </section>

          <section className="domains-section" id="domains">
            <div className="section-heading">
              <div>
                <p className="eyebrow">YOUR DATA UNIVERSE</p>
                <h2>Choose a domain.</h2>
              </div>

              <p>
                Each domain provides a dedicated analytical workspace designed
                around its own data.
              </p>
            </div>

            <div className="domain-grid">
              {Object.entries(domains).map(([key, item], index) => (
                <button
                  className={`domain-card ${item.accent}`}
                  key={key}
                  onClick={() => selectDomain(key)}
                >
                  <div className="domain-card-top">
                    <span>0{index + 1}</span>
                    <span>EXPLORE →</span>
                  </div>

                  <div className="domain-icon">
                    {key === "it" && "⌘"}
                    {key === "retail" && "◈"}
                    {key === "airline" && "✦"}
                  </div>

                  <div className="domain-card-content">
                    <p>{item.shortName}</p>
                    <h3>{item.name}</h3>
                    <span>{item.subtitle}</span>
                  </div>
                </button>
              ))}
            </div>
          </section>

          <section className="how-section" id="how-it-works">
            <div className="section-heading centered">
              <p className="eyebrow">THE PROCESS</p>
              <h2>From question to insight.</h2>
            </div>

            <div className="process-grid">
              <div className="process-item">
                <span>01</span>
                <h3>Ask</h3>
                <p>
                  Type a question in simple natural language. No SQL knowledge
                  required.
                </p>
              </div>

              <div className="process-item">
                <span>02</span>
                <h3>Generate</h3>
                <p>
                  The Text-to-SQL engine understands your database schema and
                  creates the appropriate SQL query.
                </p>
              </div>

              <div className="process-item">
                <span>03</span>
                <h3>Understand</h3>
                <p>
                  Validated results are returned in a clear, readable format
                  along with the generated SQL.
                </p>
              </div>
            </div>
          </section>
        </main>

        <footer className="footer">
          <div>
            <strong>T2SQL</strong>
            <span>Natural language database intelligence.</span>
          </div>

          <span>BE IT Final Year Project</span>
        </footer>
      </div>
    );
  }

  return (
    <div className={`app dashboard-app ${domain.accent}`}>
      <nav className="navbar dashboard-nav">
        <button className="brand-button" onClick={goHome}>
          T2<span>SQL</span>
        </button>

        <button className="back-button" onClick={goHome}>
          ← All Domains
        </button>

        <div className="nav-status">
          <span className="status-dot"></span>
          Database Connected
        </div>
      </nav>

      <main>
        <section className="dashboard-hero">
          <div>
            <p className="eyebrow">{domain.shortName} / INTELLIGENCE</p>

            <h1>{domain.name}</h1>

            <p className="dashboard-subtitle">{domain.subtitle}</p>

            <p className="dashboard-description">{domain.description}</p>
          </div>

          <div className="dashboard-number">
            <span>DOMAIN</span>
            <strong>
              {selectedDomain === "it"
                ? "01"
                : selectedDomain === "retail"
                  ? "02"
                  : "03"}
            </strong>
          </div>
        </section>

        <section className="metrics-grid">
          {domain.metrics.map((metric) => (
            <div className="metric-card" key={metric.label}>
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
            </div>
          ))}
        </section>

        <section className="query-section">
          <div className="query-heading">
            <div>
              <p className="eyebrow">NATURAL LANGUAGE QUERY</p>
              <h2>Ask your database.</h2>
            </div>

            <span className="query-badge">
              {domain.shortName.toUpperCase()} DATABASE
            </span>
          </div>

          <div className="query-workspace">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder={`Ask something about your ${domain.shortName.toLowerCase()} data...`}
              rows="5"
            />

            <div className="query-actions">
              <button
                className="ask-button"
                type="button"
                onClick={askQuestion}
                disabled={loading}
              >
                {loading ? "PROCESSING..." : "ASK DATABASE →"}
              </button>

              <button
                className="clear-button"
                type="button"
                onClick={clearAll}
                disabled={loading}
              >
                Clear
              </button>
            </div>
          </div>
        </section>

        <section className="examples-section">
          <div className="examples-heading">
            <p className="eyebrow">GET STARTED</p>
            <h2>Try a question.</h2>
          </div>

          <div className="example-grid">
            {domain.examples.map((example, index) => (
              <button
                className="example-card"
                key={example}
                onClick={() => selectExample(example)}
              >
                <span>0{index + 1}</span>
                <strong>{example}</strong>
                <em>→</em>
              </button>
            ))}
          </div>
        </section>

        {error && (
          <section className="output-section">
            <div className="output-heading">
              <p className="eyebrow">SYSTEM MESSAGE</p>
              <h2>Something went wrong.</h2>
            </div>

            <div className="error-output">{error}</div>
          </section>
        )}

        {answer && (
          <section className="output-section">
            <div className="output-heading">
              <p className="eyebrow">QUERY RESPONSE</p>
              <h2>Here's what we found.</h2>
            </div>

            <div className="answer-output">
              <span>ANSWER</span>
              <p>{answer}</p>
            </div>
          </section>
        )}

        {sql && (
          <section className="output-section">
            <div className="output-heading">
              <p className="eyebrow">GENERATED QUERY</p>
              <h2>SQL generated by the model.</h2>
            </div>

            <pre className="sql-output">{sql}</pre>
          </section>
        )}

        {data && (
          <section className="output-section">
            <div className="output-heading results-heading">
              <div>
                <p className="eyebrow">DATABASE OUTPUT</p>
                <h2>Query results.</h2>
              </div>

              <span>{data.row_count} ROWS</span>
            </div>

            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    {data.columns.map((column) => (
                      <th key={column}>{column}</th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {data.rows.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      {row.map((value, columnIndex) => (
                        <td key={columnIndex}>
                          {String(value ?? "")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <div>
          <strong>T2SQL</strong>
          <span>{domain.name}</span>
        </div>

        <button onClick={goHome}>← Explore another domain</button>
      </footer>
    </div>
  );
}

export default App;