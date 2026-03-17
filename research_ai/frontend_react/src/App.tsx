import { BrowserRouter, Routes, Route, NavLink, Navigate, Outlet, Link, useSearchParams } from 'react-router-dom';
import { 
  Library, 
  FileText, 
  Sparkles,
  Search,
  TrendingUp,
  Compass,
  PencilRuler,
  PenTool,
  Microscope,
  Cpu,
  Globe,
  ShieldCheck,
  BarChart3
} from 'lucide-react';

import LandingPage from './pages/LandingPage';
import LiteratureReview from './pages/LiteratureReview';
import PaperReader from './pages/PaperReader';
import ResearchExplorer from './pages/ResearchExplorer';
import TrendAnalytics from './pages/TrendAnalytics';
import GapFinder from './pages/GapFinder';
import MethodPlanner from './pages/MethodPlanner';
import ProposalGenerator from './pages/ProposalGenerator';
import NoveltyAnalyzer from './pages/NoveltyAnalyzer';
import AgentOrchestrator from './pages/AgentOrchestrator';
import GraphGenerators from './pages/GraphGenerators';
import LandscapePanels from './pages/LandscapePanels';
import ResponsibleAI from './pages/ResponsibleAI';
import ErrorBoundary from './components/ErrorBoundary';

// Wrapper for the dashboard that includes the sidebar
const DashboardLayout = () => {
  return (
    <div className="app-container">
      <aside className="sidebar">
        <Link to="/" style={{ textDecoration: 'none', cursor: 'pointer' }}>
          <div className="sidebar-logo">
            <Sparkles size={28} color="#6366f1" style={{ filter: 'drop-shadow(0 0 8px rgba(99, 102, 241, 0.6))' }} />
            <span style={{ 
              background: 'linear-gradient(to right, #ffffff, #94a3b8)', 
              WebkitBackgroundClip: 'text', 
              WebkitTextFillColor: 'transparent',
              fontSize: '1.6rem'
            }}>ResearchNex</span>
          </div>
        </Link>
        
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          
          <div style={{ color: '#475569', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', margin: '1rem 1rem 0.5rem' }}>
            Discovery
          </div>
          
          <NavLink to="/app/explorer" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <Search size={18} /> Research Explorer
          </NavLink>
          <NavLink to="/app/trends" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <TrendingUp size={18} /> Trend Analytics
          </NavLink>
          <NavLink to="/app/gaps" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <Compass size={18} /> Gap Finder
          </NavLink>
          
          <div style={{ color: '#475569', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', margin: '1rem 1rem 0.5rem' }}>
            Analysis
          </div>
          
          <NavLink to="/app/literature-review" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <Library size={18} /> Literature Review
          </NavLink>
          <NavLink to="/app/paper-reader" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <FileText size={18} /> Paper Reader
          </NavLink>
          <NavLink to="/app/landscape" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <Globe size={18} /> Intelligence Panel
          </NavLink>
          
          <div style={{ color: '#475569', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', margin: '1rem 1rem 0.5rem' }}>
            Synthesis
          </div>
          
          <NavLink to="/app/method-planner" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <PencilRuler size={18} /> Method Planner
          </NavLink>
          <NavLink to="/app/proposal" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <PenTool size={18} /> Grant Proposal
          </NavLink>
          <NavLink to="/app/novelty" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <Microscope size={18} /> Novelty Check
          </NavLink>
          
          <div style={{ color: '#475569', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', margin: '1rem 1rem 0.5rem' }}>
            Autonomous
          </div>
          
          <NavLink to="/app/orchestrator" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <Cpu size={18} /> Agent Swarm
          </NavLink>
          <NavLink to="/app/graphs" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
            <BarChart3 size={18} /> Graph Generator
          </NavLink>

          <div style={{ color: '#475569', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', margin: '1rem 1rem 0.5rem' }}>
            Ethics
          </div>

          <NavLink to="/app/rai" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`} style={({ isActive }) => isActive ? { borderColor: 'rgba(16,185,129,0.3)', background: 'rgba(16,185,129,0.08)' } : {}}>
            <ShieldCheck size={18} style={{ color: '#10b981' }} /> Ethics Shield
          </NavLink>

        </nav>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Landing Page */}
        <Route path="/" element={<LandingPage />} />
        
        {/* Protected/Dashboard Routes */}
        <Route path="/app" element={<DashboardLayout />}>
          <Route index element={<Navigate to="/app/explorer" replace />} />
          <Route path="explorer" element={<ErrorBoundary><ResearchExplorer /></ErrorBoundary>} />
          <Route path="trends" element={<ErrorBoundary><TrendAnalytics /></ErrorBoundary>} />
          <Route path="gaps" element={<ErrorBoundary><GapFinder /></ErrorBoundary>} />
          <Route path="literature-review" element={<ErrorBoundary><LiteratureReview /></ErrorBoundary>} />
          <Route path="paper-reader" element={<ErrorBoundary><PaperReader /></ErrorBoundary>} />
          <Route path="landscape" element={<ErrorBoundary><LandscapePanels /></ErrorBoundary>} />
          <Route path="method-planner" element={<ErrorBoundary><MethodPlanner /></ErrorBoundary>} />
          <Route path="proposal" element={<ErrorBoundary><ProposalGenerator /></ErrorBoundary>} />
          <Route path="novelty" element={<ErrorBoundary><NoveltyAnalyzer /></ErrorBoundary>} />
          <Route path="orchestrator" element={<ErrorBoundary><AgentOrchestrator /></ErrorBoundary>} />
          <Route path="graphs" element={<ErrorBoundary><GraphGenerators /></ErrorBoundary>} />
          <Route path="rai" element={<ErrorBoundary><ResponsibleAI /></ErrorBoundary>} />
        </Route>
        
        {/* Fallback to legacy routes mapping them to new routes while preserving search params */}
        <Route path="/explorer" element={<NavigateWithParams to="/app/explorer" />} />
        <Route path="/trends" element={<NavigateWithParams to="/app/trends" />} />
        <Route path="/gaps" element={<NavigateWithParams to="/app/gaps" />} />
      </Routes>
    </BrowserRouter>
  );
}

// Helper to preserve search params during redirection
const NavigateWithParams = ({ to }: { to: string }) => {
  const [searchParams] = useSearchParams();
  return <Navigate to={`${to}${searchParams.size > 0 ? '?' + searchParams.toString() : ''}`} replace />;
};

export default App;
