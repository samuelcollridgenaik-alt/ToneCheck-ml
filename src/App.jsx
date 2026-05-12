import { useEffect, useId, useState } from 'react';
import { analyzeComment, fetchBackendStatus } from './lib/api';

const initialComment = '';

const bootRevealDelay = 900;
const bootDismissDelay = 1700;

function App() {
  const textareaId = useId();
  const [comment, setComment] = useState(initialComment);
  const [result, setResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isInterfaceVisible, setIsInterfaceVisible] = useState(false);
  const [isBootDismissed, setIsBootDismissed] = useState(false);
  const [error, setError] = useState('');
  const [backendStatus, setBackendStatus] = useState({
    label: 'Checking Backend',
    tone: 'live-badge',
  });

  useEffect(() => {
    const revealTimer = window.setTimeout(() => {
      setIsInterfaceVisible(true);
    }, bootRevealDelay);

    const dismissTimer = window.setTimeout(() => {
      setIsBootDismissed(true);
    }, bootDismissDelay);

    return () => {
      window.clearTimeout(revealTimer);
      window.clearTimeout(dismissTimer);
    };
  }, []);

  useEffect(() => {
    let isActive = true;

    const loadBackendStatus = async () => {
      try {
        const health = await fetchBackendStatus();
        if (!isActive) {
          return;
        }

        setBackendStatus({
          label: health.modelLoaded ? 'Local Model Ready' : 'Local Model Online',
          tone: 'live-badge live-badge--ready',
        });
      } catch (statusError) {
        if (!isActive) {
          return;
        }

        setBackendStatus({
          label: 'Backend Offline',
          tone: 'live-badge live-badge--offline',
        });
      }
    };

    loadBackendStatus();

    return () => {
      isActive = false;
    };
  }, []);

  const trimmedComment = comment.trim();
  const metrics = {
    characters: trimmedComment.length,
    words: trimmedComment ? trimmedComment.split(/\s+/).length : 0,
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!trimmedComment) {
      setError('Paste a comment first so the analyzer has something to review.');
      setResult(null);
      return;
    }

    setError('');
    setIsAnalyzing(true);

    try {
      const moderationResult = await analyzeComment(trimmedComment);
      setResult(moderationResult);
      setBackendStatus({
        label: 'Local Model Ready',
        tone: 'live-badge live-badge--ready',
      });
    } catch (submissionError) {
      setError(
        `${submissionError.message} Start the ML backend with ./backend.sh or ./ml-dev.sh and try again.`,
      );
      setResult(null);
      setBackendStatus({
        label: 'Backend Offline',
        tone: 'live-badge live-badge--offline',
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const statusTone = result?.isToxic ? 'status-pill--danger' : 'status-pill--safe';
  const meterTone = result?.isToxic ? 'meter-fill--danger' : 'meter-fill--safe';

  return (
    <>
      <div className={`app-shell ${isInterfaceVisible ? 'app-shell--visible' : ''}`}>
        <main className="layout">
          <section className="hero">
            <div className="hero-copy">
              <span className="eyebrow">Local ML Moderation</span>
              <h1>Flag toxic comments with a polished, local-first moderation flow.</h1>
              <p className="hero-text">
                ToneCheck connects to a local Python inference service so the
                interface stays clean while the moderation decision comes from a
                real toxicity model running on your machine.
              </p>
            </div>

            <div className="hero-panel">
              <form className="analyzer-card" onSubmit={handleSubmit}>
                <div className="card-header">
                  <div>
                    <p className="card-label">Comment Input</p>
                    <h2>Analyze a social media comment</h2>
                  </div>
                  <span className={backendStatus.tone}>{backendStatus.label}</span>
                </div>

                <label className="sr-only" htmlFor={textareaId}>
                  Comment input
                </label>
                <textarea
                  id={textareaId}
                  className="comment-box"
                  value={comment}
                  onChange={(event) => setComment(event.target.value)}
                  placeholder="Paste a comment here..."
                  rows={7}
                />

                <div className="form-footer">
                  <div className="metric-row">
                    <span>{metrics.characters} characters</span>
                    <span>{metrics.words} words</span>
                  </div>

                  <button className="submit-button" type="submit" disabled={isAnalyzing}>
                    <span>{isAnalyzing ? 'Analyzing...' : 'Analyze Comment'}</span>
                    <span className="button-glow" aria-hidden="true" />
                  </button>
                </div>

                {error ? (
                  <p className="error-text" role="alert">
                    {error}
                  </p>
                ) : null}
              </form>
            </div>
          </section>

          <section className="results-section">
            <div className={`results-card ${result ? 'results-card--active' : ''}`}>
              <div className="results-header">
                <div>
                  <p className="card-label">Moderation Result</p>
                  <h2>Decision snapshot</h2>
                </div>

                {result ? (
                  <span className={`status-pill ${statusTone}`}>{result.verdict}</span>
                ) : (
                  <span className="status-pill">Awaiting input</span>
                )}
              </div>

              {isAnalyzing ? (
                <div className="processing-state" aria-live="polite">
                  <div className="spinner" aria-hidden="true" />
                  <div>
                    <h3>Reviewing tone and language...</h3>
                    <p>
                      Sending the comment to the local ML backend while the model
                      scores toxicity categories and prepares a moderation summary.
                    </p>
                  </div>
                </div>
              ) : result ? (
                <div className="result-state" aria-live="polite">
                  <div className="score-wrap">
                    <div className="score-main">
                      <span className="score-value">{result.score}</span>
                      <span className="score-caption">toxicity score</span>
                    </div>

                    <div className="meter">
                      <div
                        className={`meter-fill ${meterTone}`}
                        style={{ width: `${result.score}%` }}
                      />
                    </div>
                  </div>

                  <div className="detail-grid">
                    <article className="detail-card">
                      <p className="detail-label">Confidence</p>
                      <strong>{result.confidence}%</strong>
                    </article>

                    <article className="detail-card">
                      <p className="detail-label">Primary Signal</p>
                      <strong>{result.primarySignal}</strong>
                    </article>

                    <article className="detail-card">
                      <p className="detail-label">Model</p>
                      <strong>{result.model}</strong>
                    </article>
                  </div>

                  <div className="message-card">
                    <h3>{result.summary}</h3>
                    <p>{result.recommendation}</p>
                  </div>

                  <div className="signal-list" aria-label="Detected signals">
                    {result.categories.slice(0, 5).map((category) => (
                      <span className="signal-chip" key={category.rawLabel}>
                        {category.label} {category.score}%
                      </span>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-orb" aria-hidden="true" />
                  <h3>Ready to evaluate</h3>
                  <p>
                    Submit a comment to see a model-backed toxicity decision, a
                    confidence estimate, and the categories that influenced it.
                  </p>
                </div>
              )}
            </div>
          </section>
        </main>
      </div>

      {!isBootDismissed ? (
        <div
          className={`loading-screen ${
            isInterfaceVisible ? 'loading-screen--dismissed' : ''
          }`}
          aria-hidden="true"
        >
          <div className="loading-core">
            <div className="loading-mark">
              <span className="mark-ring mark-ring--outer" />
              <span className="mark-ring mark-ring--inner" />
            </div>
            <p className="loading-label">ToneCheck</p>
          </div>
        </div>
      ) : null}
    </>
  );
}

export default App;
