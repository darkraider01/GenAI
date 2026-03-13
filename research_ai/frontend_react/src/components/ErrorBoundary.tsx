import { Component, type ReactNode } from 'react';

interface Props { children: ReactNode; }
interface State { hasError: boolean; error: Error | null; }

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', height: '100%', gap: '1rem', padding: '2rem', textAlign: 'center'
        }}>
          <div style={{ fontSize: '3rem' }}>⚠️</div>
          <h2 style={{ color: 'white', borderBottom: 'none' }}>Something went wrong</h2>
          <p style={{ color: 'var(--text-muted)', maxWidth: '500px', fontSize: '0.9rem' }}>
            {this.state.error?.message ?? 'An unexpected error occurred in this panel.'}
          </p>
          <button
            className="btn"
            onClick={() => this.setState({ hasError: false, error: null })}
            style={{ marginTop: '1rem' }}
          >
            Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
