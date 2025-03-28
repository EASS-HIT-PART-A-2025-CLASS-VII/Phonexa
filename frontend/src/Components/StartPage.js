import React from "react";
import "@fontsource/poppins/700.css";
import "@fontsource/poppins/400.css";
import "./Styling/StartPage.css";
import PhonexaLogo from "../ProjectImages/PhonexaLogo.png";
import { useNavigate } from "react-router-dom";

const StartPage = () => {
  const navigate = useNavigate();

  const fetchSentence = async () => {
    try {
      const response = await fetch("https://api.mistral.ai/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${process.env.REACT_APP_API_KEY}`, // Ensure you have your API key set in your environment variables
        },
        body: JSON.stringify({
          model: "mistral-small-latest",
          messages: [
            { role: "system", content: "You are a sentence generating machine, that provides no further context" },
            { role: "user", content: "Generate a random basic sentence for pronunciation evaluation," },
          ],
          temperature: 0.7,
          max_tokens: 50,
          top_p: 1.0,
          stream: false,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const generatedText = data.choices?.[0]?.message?.content || "Error generating sentence.";
      navigate("/game", { state: { sentence: generatedText } });
    } catch (error) {
      console.error("Error fetching sentence:", error);
      navigate("/game", { state: { sentence: "Error generating sentence." } });
    }
  };

  return (
    <div className="start-page">
      <img src={PhonexaLogo} alt="Phonexa Logo" className="logo" />
      <h1 className="title">Phonexa</h1>
      <p className="score">Highest Score: 0</p>
      <button className="start-button" onClick={fetchSentence}>START</button>
    </div>
  );
};

export default StartPage;