import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./Styling/LevelResult.css";

const LevelResult = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { score = 0, feedback = "No feedback available.", sentence = "No sentence provided.", audioBlob } = location.state || {};

  // Function to retry the level
  const retryLevel = () => {
    navigate("/level", { state: { sentence } });
  };

  // Function to fetch a new sentence for the next level
  const fetchNextSentence = async () => {
    try {
      const response = await fetch("https://api.mistral.ai/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${process.env.REACT_APP_API_KEY}`,
        },
        body: JSON.stringify({
          model: "mistral-small-latest",
          messages: [
            { role: "system", content: "You are a sentence generating machine, that provides no further context" },
            { role: "user", content: `Generate an advanced sentence based on the following feedback: ${feedback}` },
          ],
          temperature: 0.7,
          max_tokens: 50,
          top_p: 1.0,
          stream: false,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const newSentence = data.choices?.[0]?.message?.content || "Error generating sentence.";
        navigate("/level", { state: { sentence: newSentence } });
      } else {
        console.error("Failed to fetch new sentence.");
      }
    } catch (error) {
      console.error("Error fetching new sentence:", error);
    }
  };

  return (
    <div className="game-page">
      <div className="result-card">
        <h1 className="title">Your Results</h1>
        <p className="score">Score: <span>{score}/100</span></p>

        {/* Feedback Section */}
        <h2>Feedback:</h2>
        <div className="feedback-box">
          <p>{feedback}</p>
        </div>

        {/* Sentence Section */}
        <h2>Sentence:</h2>
        <p className="sentence-text">{sentence}</p>

        {/* Recording Section */}
        <div className="recording-container">
          <h2 className="recording-title">Your Attempt</h2>
          {audioBlob ? (
            <audio controls src={URL.createObjectURL(audioBlob)} className="audio-player">
              Your browser does not support the audio element.
            </audio>
          ) : (
            <p>No audio available.</p>
          )}
        </div>

        {/* Buttons */}
        <div className="result-actions">
          <button className="retry-button" onClick={retryLevel}>
            Retry
          </button>
          <button className="next-button" onClick={fetchNextSentence}>
            Next Level
          </button>
        </div>
      </div>
    </div>
  );
};

export default LevelResult;