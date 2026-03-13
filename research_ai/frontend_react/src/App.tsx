import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { 
  Library, 
  FileText, 
  Network, 
  Sparkles,
  Search,
  TrendingUp,
  Compass,
  PencilRuler,
  PenTool,
  Microscope,
  Cpu,
  Globe
} from 'lucide-react';

import LiteratureReview from './pages/LiteratureReview';
import PaperReader from './pages/PaperReader';
import CitationGraph from './pages/CitationGraph';
import ResearchExplorer from './pages/ResearchExplorer';
import TrendAnalytics from './pages/TrendAnalytics';
import GapFinder from './pages/GapFinder';
import MethodPlanner from './pages/MethodPlanner';
import ProposalGenerator from './pages/ProposalGenerator';
import NoveltyAnalyzer from './pages/NoveltyAnalyzer';
import AgentOrchestrator from './pages/AgentOrchestrator';
import LandscapePanels from './pages/LandscapePanels';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <aside className="sidebar">
          <div className="sidebar-logo">
            <Sparkles size={24} color="#3b82f6" />
            Research AI
          </div>
          
          <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            
            <div style={{ color: '#475569', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', margin: '1rem 1rem 0.5rem' }}>
              Discovery
            </div>
            
            <NavLink to="/explorer" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
              <Search size={18} /> Research Explorer
            </NavLink>
            <NavLink to="/trends" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
              <TrendingUp size={18} /> Trend Analytics
            </NavLink>
            <NavLink to="/gaps" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
              <Compass size={18} /> Gap Finder
            </NavLink>
            
            <div style={{ color: '#475569', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', margin: '1rem 1rem 0.5rem' }}>
              Analysis
            </div>
            
            <NavLink to="/literature-review" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
              <Library size={18} /> Literature Review
            </NavLink>
            <NavLink to="/paper-reader" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
              <FileText size={18} /> Paper Reader
            </NavLink>
            <NavLink to="/citation-graph" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
              <Network size={18} /> Citation Graph
            </NavLink>
            <NavLink to="/landscape" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
              <Globe size={18} /> Intelligence Panel
            </NavLink>
            
            <div style={{ color: '#475569', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', margin: '1rem 1rem 0.5rem' }}>
              Synthesis
            </div>
            
            <NavLink to="/method-planner" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
              <PencilRuler size={18} /> Method Planner
            </NavLink>
            <NavLink to="/proposal" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
              <PenTool size={18} /> Grant Proposal
            </NavLink>
            <NavLink to="/novelty" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
              <Microscope size={18} /> Novelty Check
            </NavLink>
            
            <div style={{ color: '#475569', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', margin: '1rem 1rem 0.5rem' }}>
              Autonomous
            </div>
            
            <NavLink to="/orchestrator" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>
              <Cpu size={18} /> Agent Swarm
            </NavLink>

          </nav>
        </aside>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/explorer" replace />} />
            <Route path="/explorer" element={<ErrorBoundary><ResearchExplorer /></ErrorBoundary>} />
            <Route path="/trends" element={<ErrorBoundary><TrendAnalytics /></ErrorBoundary>} />
            <Route path="/gaps" element={<ErrorBoundary><GapFinder /></ErrorBoundary>} />
            <Route path="/literature-review" element={<ErrorBoundary><LiteratureReview /></ErrorBoundary>} />
            <Route path="/paper-reader" element={<ErrorBoundary><PaperReader /></ErrorBoundary>} />
            <Route path="/citation-graph" element={<ErrorBoundary><CitationGraph /></ErrorBoundary>} />
            <Route path="/landscape" element={<ErrorBoundary><LandscapePanels /></ErrorBoundary>} />
            <Route path="/method-planner" element={<ErrorBoundary><MethodPlanner /></ErrorBoundary>} />
            <Route path="/proposal" element={<ErrorBoundary><ProposalGenerator /></ErrorBoundary>} />
            <Route path="/novelty" element={<ErrorBoundary><NoveltyAnalyzer /></ErrorBoundary>} />
            <Route path="/orchestrator" element={<ErrorBoundary><AgentOrchestrator /></ErrorBoundary>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
