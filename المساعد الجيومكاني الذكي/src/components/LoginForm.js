import React, { useState } from "react";
import api from "../api/api";

const LoginForm = ({ setLoggedIn }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // لوحة الألوان الجديدة المتناسقة
  const colors = {
    bg_creamy: "#F1F3E0",
    light_green: "#D2DCB6",
    mid_green: "#A1BC98",
    dark_green: "#778873",
    accent_orange: "#E67E51", 
    white: "#ffffff"
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.post("/login", { username, password });
      setLoggedIn(true);
    } catch (err) {
      setError("اسم المستخدم أو كلمة المرور غير صحيحة");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-wrapper" style={{ 
      display: "flex", 
      justifyContent: "center", 
      alignItems: "center", 
      width: "100vw",        
      minHeight: "100vh",    
      direction: "rtl",
      backgroundColor: colors.bg_creamy, 
      margin: 0,             
      padding: 0
    }}>
      <div className="card" style={{ 
        width: "90%", 
        maxWidth: "420px", 
        padding: "40px 30px", 
        borderRadius: "20px", 
        boxShadow: "0 15px 35px rgba(119, 136, 115, 0.15)", 
        backgroundColor: colors.white,
        border: `1px solid ${colors.light_green}`,
        zIndex: 1 
      }}>
        <div style={{ textAlign: "center", marginBottom: "35px" }}>
          <h1 style={{ 
            color: colors.dark_green, 
            marginBottom: "10px", 
            fontSize: "2rem", 
            fontWeight: "800" 
          }}>
            تسجيل الدخول
          </h1>
          <p style={{ color: colors.mid_green, fontSize: "1rem", fontWeight: "500" }}>
            نظام التقييم البيئي الذكي
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "20px" }}>
            <label style={{ 
              display: "block", 
              marginBottom: "10px", 
              fontWeight: "bold", 
              color: colors.dark_green,
              textAlign: "right" 
            }}>
              اسم المستخدم
            </label>
            <input
              style={{
                width: "100%",
                padding: "15px",
                borderRadius: "12px",
                border: "none",
                backgroundColor: "#E8F0FE", 
                fontSize: "1rem",
                textAlign: "center",
                outlineColor: colors.mid_green,
                boxSizing: "border-box" 
              }}
              placeholder="أدخل اسم المستخدم"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div style={{ marginBottom: "30px" }}>
            <label style={{ 
              display: "block", 
              marginBottom: "10px", 
              fontWeight: "bold", 
              color: colors.dark_green,
              textAlign: "right"
            }}>
              كلمة المرور
            </label>
            <input
              style={{
                width: "100%",
                padding: "15px",
                borderRadius: "12px",
                border: "none",
                backgroundColor: "#E8F0FE",
                fontSize: "1rem",
                textAlign: "center",
                outlineColor: colors.mid_green,
                boxSizing: "border-box"
              }}
              placeholder="••••••••"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button 
            type="submit" 
            disabled={loading}
            style={{
              width: "100%",
              padding: "15px",
              backgroundColor: loading ? colors.mid_green : colors.accent_orange,
              color: "white",
              border: "none",
              borderRadius: "12px",
              fontSize: "1.2rem",
              fontWeight: "bold",
              cursor: loading ? "not-allowed" : "pointer",
              transition: "all 0.3s ease",
              boxShadow: `0 4px 15px ${colors.accent_orange}44`
            }}
            onMouseOver={(e) => !loading && (e.target.style.backgroundColor = colors.dark_green)}
            onMouseOut={(e) => !loading && (e.target.style.backgroundColor = colors.accent_orange)}
          >
            {loading ? "جاري التحقق..." : "دخول للنظام"}
          </button>

          {error && (
            <div style={{ 
              marginTop: "20px", 
              padding: "12px", 
              backgroundColor: "#FFF5F5", 
              color: "#C53030", 
              borderRadius: "10px",
              textAlign: "center",
              fontSize: "0.9rem",
              border: "1px solid #FEB2B2"
            }}>
              ⚠️ {error}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default LoginForm;