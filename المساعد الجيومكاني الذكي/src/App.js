import React, { useState, useEffect } from 'react';
import './App.css';
import MainPortal from './layouts/MainPortal'; 
import LoginForm from "./components/LoginForm";

function App() {
  const [loggedIn, setLoggedIn] = useState(true);

  useEffect(() => {
    
    document.documentElement.dir = "rtl";
    document.documentElement.lang = "ar";
    document.body.style.backgroundColor = "#f7fafc";
  }, []);

  return (
    <div className="app-container" style={{ minHeight: "100vh" }}>
      {loggedIn ? (
        
        <MainPortal setLoggedIn={setLoggedIn} />
      ) : (
        <div className="login-wrapper" style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
          <LoginForm setLoggedIn={setLoggedIn} />
        </div>
      )}
    </div>
  );
}

export default App;