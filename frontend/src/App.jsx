
/* eslint-disable no-undef */
/* eslint-disable no-unused-vars */
import { useState } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

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

function getChartType(data) {
  if (!data || !data.columns || !data.rows) {
    return null;
  }

  if (data.columns.length !== 2 || data.rows.length === 0) {
    return null;
  }

  const firstValues = data.rows.map((row) => row[0]);
  const secondValues = data.rows.map((row) => row[1]);

  const numericSecondColumn = secondValues.every(
    (value) =>
      value !== null &&
      value !== "" &&
      !Number.isNaN(Number(value))
  );

  if (!numericSecondColumn) {
    return null;
  }

  const firstColumnLooksLikeDate = firstValues.every((value) => {
    if (!value) return false;

    const stringValue = String(value);

    return (
      /^\d{4}-\d{2}-\d{2}$/.test(stringValue) ||
      /^\d{4}-\d{2}$/.test(stringValue) ||
      /^\d{4}$/.test(stringValue)
    );
  });

  if (firstColumnLooksLikeDate) {
    return "line";
  }

  return "bar";
}

function App() {
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sql, setSql] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [executionTime, setExecutionTime] = useState(null);
  const [corrected, setCorrected] = useState(false);
  const [originalSql, setOriginalSql] = useState("");
  const [sessionId] = useState(() => crypto.randomUUID());

  // Query History
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Schema Visualization
  const [schema, setSchema] = useState(null);
  const [schemaLoading, setSchemaLoading] = useState(false);
  const [schemaError, setSchemaError] = useState("");

  const domain = selectedDomain ? domains[selectedDomain] : null;
  const chartType = getChartType(data);

  // Load query history from backend
  const loadHistory = async () => {
    setHistoryLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/history?limit=20"
      );

      const result = await response.json();

      if (result.success) {
        setHistory(result.history || []);
      }
    } catch (err) {
      console.error("Could not load query history:", err);
    } finally {
      setHistoryLoading(false);
    }
  };

  // Load database schema from backend
  const loadSchema = async () => {
    setSchemaLoading(true);
    setSchemaError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/schema"
      );

      if (!response.ok) {
        throw new Error("Schema request failed.");
      }

      const result = await response.json();

      setSchema(result);
    } catch (err) {
      console.error("Could not load database schema:", err);
      setSchemaError(
        "Could not load database schema. Make sure FastAPI is running."
      );
    } finally {
      setSchemaLoading(false);
    }
  };

  const selectDomain = (domainKey) => {
    setSelectedDomain(domainKey);
    setQuestion("");
    setAnswer("");
    setSql("");
    setData(null);
    setError("");
    setExecutionTime(null);
    setCorrected(false);
    setOriginalSql("");

    loadHistory();
    loadSchema();
  };

  const goHome = () => {
    setSelectedDomain(null);
    setQuestion("");
    setAnswer("");
    setSql("");
    setData(null);
    setError("");
    setExecutionTime(null);
    setCorrected(false);
    setOriginalSql("");
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
    setExecutionTime(null);
    setCorrected(false);
    setOriginalSql("");
  };

  const askQuestion = async () => {
    if (!question.trim()) {
      setError("Please enter a question.");
      setExecutionTime(null);
      return;
    }

    setLoading(true);
    setAnswer("");
    setSql("");
    setData(null);
    setError("");
    setExecutionTime(null);
    setCorrected(false);
    setOriginalSql("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/query?question=" +
          encodeURIComponent(question) +
          "&domain=" +
          encodeURIComponent(selectedDomain) +
          "&session_id=" +
          encodeURIComponent(sessionId),
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
      setExecutionTime(result.execution_time_ms);
      setCorrected(result.corrected === true);
      setOriginalSql(result.original_sql || "");

      await loadHistory();
    } catch (err) {
      setError(
        "Could not connect to the backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // HOME PAGE
  // =========================

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
              <p className="eyebrow">
                NATURAL LANGUAGE DATABASE INTELLIGENCE
              </p>

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

  // =========================
  // DOMAIN DASHBOARD
  // =========================

  const currentSchema =
    schema && schema[selectedDomain]
      ? schema[selectedDomain]
      : {};

  const schemaTables = Object.entries(currentSchema);

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
            <p className="eyebrow">
              {domain.shortName} / INTELLIGENCE
            </p>

            <h1>{domain.name}</h1>

            <p className="dashboard-subtitle">
              {domain.subtitle}
            </p>

            <p className="dashboard-description">
              {domain.description}
            </p>
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

        {/* =========================
            SCHEMA VISUALIZATION
            ========================= */}

        <section className="schema-section">
          <div className="schema-heading">
            <div>
              <p className="eyebrow">DATABASE STRUCTURE</p>
              <h2>Explore the schema.</h2>
            </div>

            <button
              className="history-refresh"
              type="button"
              onClick={loadSchema}
              disabled={schemaLoading}
            >
              {schemaLoading ? "LOADING..." : "REFRESH ↻"}
            </button>
          </div>

          {schemaLoading && !schema ? (
            <div className="schema-empty">
              Loading database schema...
            </div>
          ) : schemaError ? (
            <div className="schema-empty">
              {schemaError}
            </div>
          ) : schemaTables.length === 0 ? (
            <div className="schema-empty">
              No schema information available.
            </div>
          ) : (
            <div className="schema-table-grid">
              {schemaTables.map(([tableName, tableData]) => (
                <details
                  className="schema-table-card"
                  key={tableName}
                >
                  <summary>
                    <div>
                      <span className="schema-table-label">
                        TABLE
                      </span>

                      <strong>{tableName}</strong>
                    </div>

                    <span className="schema-column-count">
                      {tableData.columns.length} COLUMNS
                    </span>
                  </summary>

                  <div className="schema-table-content">
                    <div className="schema-columns">
                      <div className="schema-subheading">
                        <span>COLUMN</span>
                        <span>TYPE</span>
                        <span>NULLABLE</span>
                      </div>

                      {tableData.columns.map((column) => (
                        <div
                          className="schema-column-row"
                          key={column.name}
                        >
                          <strong>{column.name}</strong>
                          <span>{column.type}</span>
                          <span>
                            {column.nullable ? "YES" : "NO"}
                          </span>
                        </div>
                      ))}
                    </div>

                    {tableData.relationships &&
                      tableData.relationships.length > 0 && (
                        <div className="schema-relationships">
                          <div className="schema-subheading">
                            <span>RELATIONSHIPS</span>
                          </div>

                          {tableData.relationships.map(
                            (relationship, index) => (
                              <div
                                className="schema-relationship-row"
                                key={`${relationship.column}-${index}`}
                              >
                                <strong>
                                  {relationship.column}
                                </strong>

                                <span>→</span>

                                <span>
                                  {relationship.references_schema}.
                                  {relationship.references_table}.
                                  {relationship.references_column}
                                </span>
                              </div>
                            )
                          )}
                        </div>
                      )}
                  </div>
                </details>
              ))}
            </div>
          )}
        </section>

        {/* =========================
            QUERY WORKSPACE
            ========================= */}

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

        {/* =========================
            ANSWER
            ========================= */}

        {error && (
          <section className="output-section answer-section">
            <div className="output-heading">
              <p className="eyebrow">SYSTEM MESSAGE</p>
              <h2>Something went wrong.</h2>
            </div>

            <div className="error-output">{error}</div>
          </section>
        )}

        {answer && (
          <section className="output-section answer-section">
            <div className="output-heading">
              <p className="eyebrow">QUERY RESPONSE</p>
              <h2>Here's what we found.</h2>
            </div>

            <div className="answer-output">
              <span>ANSWER</span>
              <p>{answer}</p>
            </div>

            {executionTime !== null && (
              <div className="performance-info">
                <span>QUERY EXECUTION</span>
                <strong>
                  {executionTime.toFixed(2)} ms
                </strong>
              </div>
            )}

            {corrected && (
              <div className="correction-info">
                <span>SQL CORRECTION</span>
                <strong>Automatically corrected</strong>
              </div>
            )}

            {corrected && originalSql && (
              <div className="sql-comparison">
                <div className="sql-comparison-header">
                  <span>SQL COMPARISON</span>
                  <strong>Original → Corrected</strong>
                </div>

                <div className="sql-comparison-grid">
                  <div className="sql-comparison-block">
                    <span>ORIGINAL SQL</span>
                    <pre>{originalSql}</pre>
                  </div>

                  <div className="sql-comparison-block">
                    <span>CORRECTED SQL</span>
                    <pre>{sql}</pre>
                  </div>
                </div>
              </div>
            )}
          </section>
        )}

        {/* =========================
            EXAMPLE QUESTIONS
            ========================= */}

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

        {/* =========================
            GENERATED SQL
            ========================= */}

        {sql && (
          <section className="output-section">
            <div className="output-heading">
              <p className="eyebrow">GENERATED QUERY</p>
              <h2>SQL generated by the model.</h2>
            </div>

            <pre className="sql-output">{sql}</pre>
          </section>
        )}

        {/* =========================
            DATABASE RESULTS
            ========================= */}

        {data && (
          <section className="output-section">
            <div className="output-heading results-heading">
              <div>
                <p className="eyebrow">DATABASE OUTPUT</p>
                <h2>Query results.</h2>
              </div>

              <span>{data.row_count} ROWS</span>
            </div>

            {chartType && data.rows.length > 0 && (
  <div className="result-chart">
    <div className="result-chart-heading">
      <div>
        <p className="eyebrow">VISUALIZATION</p>
        <h3>
          {chartType === "bar" && "Result breakdown"}
          {chartType === "line" && "Result trend"}
          {chartType === "pie" && "Result distribution"}
        </h3>
      </div>

      <span>
        {data.columns[0]} / {data.columns[1]}
      </span>
    </div>

    <div className="chart-container">
      <ResponsiveContainer width="100%" height={360}>
        {chartType === "bar" && (
          <BarChart
            data={data.rows.map((row) => ({
              name: String(row[0] ?? ""),
              value: Number(row[1]) || 0,
            }))}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="name"
              angle={-25}
              textAnchor="end"
              height={80}
            />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" />
          </BarChart>
        )}

        {chartType === "line" && (
          <LineChart
            data={data.rows.map((row) => ({
              name: String(row[0] ?? ""),
              value: Number(row[1]) || 0,
            }))}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="value"
              strokeWidth={2}
            />
          </LineChart>
        )}

        {chartType === "pie" && (
          <PieChart>
            <Pie
              data={data.rows.map((row) => ({
                name: String(row[0] ?? ""),
                value: Number(row[1]) || 0,
              }))}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={125}
              label
            >
              {data.rows.map((_, index) => (
                <Cell key={`cell-${index}`} />
              ))}
            </Pie>

            <Tooltip />
            <Legend />
          </PieChart>
        )}
      </ResponsiveContainer>
    </div>
  </div>
)}

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

        {/* =========================
            QUERY HISTORY
            ========================= */}

        <section className="history-section">
          <div className="history-heading">
            <div>
              <p className="eyebrow">QUERY HISTORY</p>
              <h2>Previous questions.</h2>
            </div>

            <button
              className="history-refresh"
              type="button"
              onClick={loadHistory}
              disabled={historyLoading}
            >
              {historyLoading ? "LOADING..." : "REFRESH ↻"}
            </button>
          </div>

          {historyLoading && history.length === 0 ? (
            <div className="history-empty">
              Loading query history...
            </div>
          ) : history.filter(
              (item) => item.domain === selectedDomain
            ).length === 0 ? (
            <div className="history-empty">
              No {selectedDomain.toUpperCase()} queries have been recorded
              yet.
            </div>
          ) : (
            <div className="history-table-wrapper">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>QUESTION</th>
                    <th>DOMAIN</th>
                    <th>ROWS</th>
                    <th>EXECUTION</th>
                    <th>DATE</th>
                    <th>SQL</th>
                  </tr>
                </thead>

                <tbody>
                  {history
                    .filter(
                      (item) => item.domain === selectedDomain
                    )
                    .map((item, index) => (
                      <tr key={item.id}>
                        <td className="history-number">
                          {String(index + 1).padStart(2, "0")}
                        </td>

                        <td className="history-question">
                          {item.question}

                          {item.corrected && (
                            <span className="history-corrected-badge">
                              CORRECTED
                            </span>
                          )}
                        </td>

                        <td>
                          <span className="history-domain">
                            {item.domain.toUpperCase()}
                          </span>
                        </td>

                        <td>{item.row_count ?? 0}</td>

                        <td>
                          {item.execution_time_ms !== null
                            ? `${Number(
                                item.execution_time_ms
                              ).toFixed(2)} ms`
                            : "—"}
                        </td>

                        <td className="history-date">
                          {item.created_at
                            ? new Date(
                                item.created_at
                              ).toLocaleString()
                            : "—"}
                        </td>

                        <td>
                          <details className="history-sql">
                            <summary>VIEW</summary>

                            <div className="history-details">
                              <div className="history-detail-block">
                                <span>QUESTION</span>
                                <p>{item.question}</p>
                              </div>

                              {item.answer && (
                                <div className="history-detail-block">
                                  <span>ANSWER</span>
                                  <p>{item.answer}</p>
                                </div>
                              )}

                              <div className="history-detail-block">
                                <span>GENERATED SQL</span>
                                <pre>{item.sql}</pre>
                              </div>

                              {item.corrected && (
                                <div className="history-correction">
                                  <div className="history-correction-header">
                                    <span>SQL CORRECTION</span>
                                    <strong>
                                      Automatically corrected
                                    </strong>
                                  </div>

                                  <div className="history-correction-block">
                                    <span>ORIGINAL SQL</span>
                                    <pre>
                                      {item.original_sql}
                                    </pre>
                                  </div>

                                  {item.original_error && (
                                    <div className="history-correction-block">
                                      <span>DATABASE ERROR</span>
                                      <pre>
                                        {item.original_error}
                                      </pre>
                                    </div>
                                  )}

                                  <div className="history-correction-block">
                                    <span>CORRECTED SQL</span>
                                    <pre>{item.sql}</pre>
                                  </div>
                                </div>
                              )}

                              <div className="history-detail-grid">
                                <div>
                                  <span>ROWS RETURNED</span>
                                  <strong>
                                    {item.row_count}
                                  </strong>
                                </div>

                                <div>
                                  <span>EXECUTION TIME</span>
                                  <strong>
                                    {item.execution_time_ms !== null
                                      ? `${Number(
                                          item.execution_time_ms
                                        ).toFixed(2)} ms`
                                      : "N/A"}
                                  </strong>
                                </div>

                                <div>
                                  <span>CREATED AT</span>
                                  <strong>
                                    {new Date(
                                      item.created_at
                                    ).toLocaleString()}
                                  </strong>
                                </div>
                              </div>
                            </div>
                          </details>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>

      <footer className="footer">
        <div>
          <strong>T2SQL</strong>
          <span>{domain.name}</span>
        </div>

        <button onClick={goHome}>
          ← Explore another domain
        </button>
      </footer>
    </div>
  );
}

export default App;

