import React, { useState } from 'react';
import './MainPortal.css';
import Dashboard from '../pages/Dashboard'; 

const PROJECTS = {
  DASHBOARD: "http://localhost:8501", 
  LEGAL_AI: "http://127.0.0.1:8001/llm/chat" 
};

const MainPortal = ({ setLoggedIn }) => {
  const [activeTab, setActiveTab] = useState('PREDICTION');

  return (
    <div className="portal-container">
      {/* القائمة الجانبية - Sidebar */}
      <nav className="sidebar">
        <div className="sidebar-header">
          <div className="logo-icon"></div>
          <h3>نظام البيئة الذكي</h3>
        </div>
        
        <ul className="nav-links">
          <li className={activeTab === 'PREDICTION' ? 'active' : ''} 
              onClick={() => setActiveTab('PREDICTION')}>
            <span className="icon"></span> نظام التنبؤ بالمخاطر
          </li>
          
          <li className={activeTab === 'DASHBOARD' ? 'active' : ''} 
              onClick={() => setActiveTab('DASHBOARD')}>
            <span className="icon"></span> لوحة التحليلات 
          </li>
          
          <li className={activeTab === 'LEGAL_AI' ? 'active' : ''} 
              onClick={() => setActiveTab('LEGAL_AI')}>
            <span className="icon"></span> المساعد الجيومكاني (AI)
          </li>
        </ul>

        {/* تذييل القائمة الجانبية */}
        <div className="sidebar-footer">
          <button className="logout-button-sidebar" onClick={() => setLoggedIn(false)}>
            تسجيل الخروج
          </button>
          <p style={{ marginTop: '10px', fontSize: '10px' }}>إصدار 2026 v1.0</p>
        </div>
      </nav>

      {/* منطقة المحتوى الرئيسية */}
      <main className="content-area">
        {activeTab === 'PREDICTION' ? (
            <div className="embedded-component">
                <Dashboard setLoggedIn={setLoggedIn} /> 
            </div>
        ) : (
            <iframe 
                key={activeTab}
                src={PROJECTS[activeTab]} 
                title="Project View"
                className="project-iframe"
                /* التعديل الجوهري: إضافة الصلاحيات هنا */
                allow="microphone; camera; display-capture;"
            />
        )}
      </main>
    </div>
  );
};

export default MainPortal;