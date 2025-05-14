import React from "react";
import "@fontsource/poppins/700.css";
import "@fontsource/poppins/400.css";
import "./Styling/StartPage.css";
import PhonexaLogo from "../ProjectImages/PhonexaLogo.png";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

const StartPage = () => {
  const navigate = useNavigate();
  const [highestStreak, setHighestStreak] = useState(0);

  const fetchSentence = async () => {
  try {
    const response = await fetch("http://localhost:5000/generate-first-sentence", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const generatedSentence = await response.text();
    const parsedData = JSON.parse(generatedSentence);

    navigate("/level", { state: { sentence: parsedData.sentence, sentence_ipa: parsedData.sentence_ipa } });
  } catch (error) {
    console.error("Error fetching sentence:", error);
    navigate("/level", { state: { sentence: "Error generating sentence.", sentence_ipa: "Error generating IPA." } });
  }
};
  useEffect(() => {
    const current = parseInt(localStorage.getItem("phonexa_current_streak") || "0", 10);
    const highest = parseInt(localStorage.getItem("phonexa_highest_streak") || "0", 10);

    if (current > highest) {
      localStorage.setItem("phonexa_highest_streak", current);
      setHighestStreak(current);
    } else {
      setHighestStreak(highest);
    }
    localStorage.setItem("phonexa_current_streak", "0"); // Reset current streak
    localStorage.setItem("phonexa_used_animals", "[]"); // Reset used animals
  }, []);




  return (
    <div className="start-page">
      <div className="start-card">
        <img src={PhonexaLogo} alt="Phonexa Logo" className="logo" />
        <h1 className="title">Phonexa</h1>
        <h2 className="subtitle">A.I Pronunciation Game</h2>
        <p className="score">Highest Streak: {highestStreak}</p>

        {/* Instructions Section */}
        <div className="instructions-box">
          <h2>How to Play</h2>
          <ol>
            <li>Click the "START" button to begin the game.</li>
            <li>Read the sentence displayed on the screen.</li>
            <li>Record your pronunciation using the microphone button.</li>
            <li>Submit your recording to receive feedback and a score.</li>
            <li>Retry or move to the next level to improve your skills!</li>
          </ol>
        </div>

        <button className="start-button" onClick={fetchSentence}>START</button>
      </div>
    </div>
  );
};

export default StartPage;