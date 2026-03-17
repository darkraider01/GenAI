import React from 'react';
import { motion } from 'framer-motion';
import type { Variants } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  Search, 
  Network, 
  BrainCircuit, 
  FileText, 
  ShieldCheck,
  ChevronRight,
  Database,
  Cpu,
  BarChart,
  GitMerge
} from 'lucide-react';
import { AssistantChat } from '../components/AssistantChat';
import { BackgroundNetwork } from '../components/BackgroundNetwork';

const LandingPage = () => {
  const navigate = useNavigate();

  const handleLaunch = () => {
    navigate('/app');
  };

  // Animation Variants
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.2 }
    }
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
  };

  return (
    <div className="landing-container" style={{
      minHeight: '100vh',
      background: 'var(--bg-dark)',
      color: 'var(--text-main)',
      overflowX: 'hidden'
    }}>
      
      {/* Dynamic Network Background */}
      <BackgroundNetwork />

      {/* Navigation Bar */}
      <nav style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1.5rem 4rem',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
        backdropFilter: 'blur(10px)',
        position: 'fixed',
        top: 0,
        width: '100%',
        zIndex: 50
      }}>
        <div 
          onClick={() => navigate('/')} 
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '0.75rem', 
            cursor: 'pointer',
            transition: 'opacity 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.opacity = '0.8'}
          onMouseOut={(e) => e.currentTarget.style.opacity = '1'}
        >
          <Sparkles size={28} color="#6366f1" style={{ filter: 'drop-shadow(0 0 8px rgba(99, 102, 241, 0.6))' }} />
          <span style={{ 
            background: 'linear-gradient(to right, #ffffff, #94a3b8)', 
            WebkitBackgroundClip: 'text', 
            WebkitTextFillColor: 'transparent',
            fontSize: '1.6rem',
            fontWeight: 800,
            letterSpacing: '-0.5px'
          }}>ResearchNex</span>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        textAlign: 'center',
        padding: '8rem 2rem 4rem',
        position: 'relative'
      }}>
        {/* Background glow effects */}
        <div style={{
          position: 'absolute',
          top: '20%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '600px',
          height: '600px',
          background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, rgba(0,0,0,0) 70%)',
          zIndex: 0,
          pointerEvents: 'none'
        }} />

        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          style={{ zIndex: 1, maxWidth: '900px' }}
        >
          <motion.div variants={itemVariants} style={{ marginBottom: '1.5rem' }}>
            <span style={{
              background: 'rgba(99, 102, 241, 0.1)',
              color: '#a5b4fc',
              padding: '0.5rem 1rem',
              borderRadius: '99px',
              border: '1px solid rgba(99,102,241,0.3)',
              fontSize: '0.875rem',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}>Advanced AI Research Engine</span>
          </motion.div>
          
          <motion.h1 variants={itemVariants} style={{ 
            fontSize: 'clamp(3rem, 6vw, 5.5rem)', 
            lineHeight: 1.1,
            marginBottom: '1.5rem',
            background: 'linear-gradient(to bottom right, #ffffff, #a5b4fc)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            textShadow: 'none'
          }}>
            Accelerate Discovery with<br/>Autonomous Intelligence
          </motion.h1>
          
          <motion.p variants={itemVariants} style={{ 
            fontSize: '1.25rem', 
            color: 'var(--text-muted)',
            marginBottom: '3rem',
            maxWidth: '700px',
            margin: '0 auto 3rem'
          }}>
            ResearchNex combines hybrid vector retrieval, dynamic embedding clustering, and multi-agent orchestration to detect research gaps and generate literature reviews at superhuman speed.
          </motion.p>
          
          <motion.div variants={itemVariants} style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <button onClick={handleLaunch} className="btn" style={{ padding: '1rem 2.5rem', fontSize: '1.1rem' }}>
              Launch Platform
            </button>
            <button onClick={() => document.getElementById('architecture')?.scrollIntoView({ behavior: 'smooth' })} className="btn" style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: 'white' }}>
              Explore Architecture
            </button>
          </motion.div>
        </motion.div>
      </section>

      {/* Architecture Pipeline Section */}
      <section id="architecture" style={{ padding: '8rem 4rem', background: 'rgba(7,9,15,0.8)' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ fontSize: '2.5rem', border: 'none', marginBottom: '1rem' }}>Data-Driven Research Architecture</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', marginBottom: '4rem', maxWidth: '600px', margin: '0 auto 4rem' }}>
            Our transparent, multi-stage pipeline ensures explainable AI outputs backed by actual citations.
          </p>

          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '2rem', alignItems: 'center' }}>
            
            <PipelineNode icon={<Database />} title="1. Hybrid RAG" desc="Vector + BM25 Fusion" />
            <PipelineArrow />
            <PipelineNode icon={<Network />} title="2. UMAP/HDBSCAN" desc="Dynamic Topic Clustering" />
            <PipelineArrow />
            <PipelineNode icon={<Search />} title="3. Gap Detection" desc="Density & Cross-Citation Analysis" />
            <PipelineArrow />
            <PipelineNode icon={<BrainCircuit />} title="4. Multi-Agent Swarm" desc="Review & Proposal Generation" />

          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section style={{ padding: '8rem 4rem', maxWidth: '1400px', margin: '0 auto' }}>
        <h2 style={{ fontSize: '2.5rem', border: 'none', textAlign: 'center', marginBottom: '4rem' }}>Unparalleled Diagnostic Capabilities</h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem' }}>
          <FeatureCard 
            icon={<GitMerge color="#60a5fa" size={32} />}
            title="Hybrid Retrieval System"
            desc="Fuses ChromaDB vector semantic search with BM25 keyword retrieval using Reciprocal Rank Fusion (RRF) for exhaustive literature sweeps."
          />
          <FeatureCard 
            icon={<BarChart color="#c084fc" size={32} />}
            title="Data-Driven Gap Detection"
            desc="Projects embeddings via UMAP into HDBSCAN clusters. Identifies high-cosine-similarity research frontiers with low cross-citation density."
          />
          <FeatureCard 
            icon={<FileText color="#34d399" size={32} />}
            title="Explainable Generation"
            desc="Every literature review, methodology plan, and generated proposal strictly lists its supporting source papers and exact algorithmic reasoning."
          />
          <FeatureCard 
            icon={<ShieldCheck color="#fbbf24" size={32} />}
            title="Responsible AI Layer"
            desc="Evaluates generated proposals and analytics against bias, toxicity, and hallucination guardrails before human presentation."
          />
        </div>
      </section>

      {/* Tech Stack */}
      <section style={{ padding: '6rem 4rem', background: 'rgba(255,255,255,0.02)', borderTop: '1px solid rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ maxWidth: '1000px', margin: '0 auto', textAlign: 'center' }}>
          <h3 style={{ fontSize: '1.5rem', color: 'var(--text-muted)', marginBottom: '3rem', fontWeight: 500 }}>Powered by Industry Standard Technology</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '1.5rem' }}>
            <TechBadge name="React 19" />
            <TechBadge name="FastAPI" />
            <TechBadge name="Python" />
            <TechBadge name="ChromaDB" />
            <TechBadge name="BAAI/bge-large-en" />
            <TechBadge name="UMAP" />
            <TechBadge name="HDBSCAN" />
            <TechBadge name="BERTopic" />
            <TechBadge name="LangChain" />
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section style={{ padding: '8rem 2rem', textAlign: 'center' }}>
        <motion.div 
          initial={{ scale: 0.95, opacity: 0 }}
          whileInView={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          style={{
            maxWidth: '800px',
            margin: '0 auto',
            background: 'linear-gradient(145deg, rgba(30,41,59,0.7), rgba(15,23,42,0.9))',
            padding: '4rem 2rem',
            borderRadius: '32px',
            border: '1px solid rgba(99,102,241,0.2)',
            boxShadow: '0 20px 40px -10px rgba(99,102,241,0.1)'
          }}
        >
          <h2 style={{ fontSize: '2.5rem', border: 'none', marginBottom: '1.5rem' }}>Ready to Accelerate Your Research?</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '1.25rem', marginBottom: '2.5rem' }}>Join the next generation of academic discovery with ResearchNex.</p>
          <button onClick={handleLaunch} className="btn" style={{ fontSize: '1.25rem', padding: '1.25rem 3rem' }}>
            Initialize Platform
          </button>
        </motion.div>
      </section>
      
      {/* Footer */}
      <footer style={{ padding: '2rem', textAlign: 'center', borderTop: '1px solid rgba(255,255,255,0.05)', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
        &copy; {new Date().getFullYear()} ResearchNex Platform. All systems operational.
      </footer>
      
      {/* Floating AI Assistant Chat */}
      <AssistantChat />
    </div>
  );
};

// Sub-components for Landing Page
const PipelineNode = ({ icon, title, desc }: { icon: React.ReactNode, title: string, desc: string }) => (
  <motion.div 
    whileHover={{ y: -5, boxShadow: '0 10px 25px -5px rgba(99, 102, 241, 0.3)' }}
    style={{
      background: 'var(--bg-card)',
      border: '1px solid rgba(99,102,241,0.2)',
      borderRadius: '16px',
      padding: '2rem 1.5rem',
      width: '260px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '1rem',
      position: 'relative',
      zIndex: 2
    }}
  >
    <div style={{ background: 'rgba(99,102,241,0.1)', padding: '1rem', borderRadius: '50%', color: '#a5b4fc' }}>
      {icon}
    </div>
    <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'white' }}>{title}</h3>
    <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-muted)' }}>{desc}</p>
  </motion.div>
);

const PipelineArrow = () => (
  <div style={{ color: 'rgba(255,255,255,0.2)' }}>
    <ChevronRight size={32} />
  </div>
);

const FeatureCard = ({ icon, title, desc }: { icon: React.ReactNode, title: string, desc: string }) => (
  <motion.div
    whileHover={{ y: -10 }}
    style={{
      background: 'rgba(15, 23, 42, 0.4)',
      border: '1px solid rgba(255,255,255,0.05)',
      borderRadius: '24px',
      padding: '2.5rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1.5rem',
      backdropFilter: 'blur(10px)'
    }}
  >
    <div>{icon}</div>
    <h3 style={{ margin: 0, fontSize: '1.4rem', color: 'white' }}>{title}</h3>
    <p style={{ margin: 0, color: 'var(--text-muted)', lineHeight: 1.6 }}>{desc}</p>
  </motion.div>
);

const TechBadge = ({ name }: { name: string }) => (
  <div style={{
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '99px',
    padding: '0.75rem 1.5rem',
    color: '#e2e8f0',
    fontWeight: 500,
    fontSize: '0.95rem',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem'
  }}>
    <Cpu size={14} color="var(--accent)" /> {name}
  </div>
);

export default LandingPage;
