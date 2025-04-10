import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./Styling/LevelResult.css";
import SpeakerIcon from "../ProjectImages/speaker.png";

const LevelResult = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { score = 0, feedback = "No feedback available.", sentence = "No sentence provided.", audioBlob } = location.state || {};

  const [audio, setAudio] = useState(null); // State to manage the audio object
  const [isPlaying, setIsPlaying] = useState(false); // State to track if audio is playing

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

  // Function to handle text-to-speech playback
  const playTextToSpeech = async (text) => {
    if (isPlaying && audio) {
      // If audio is already playing, stop it
      audio.pause();
      audio.currentTime = 0; // Reset playback position
      setIsPlaying(false);
      return; // Exit the function to allow a second click for replay
    }

    try {
      // Fetch the audio file from the backend
      const response = await fetch("http://localhost:8000/tts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ sentence: text }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch TTS audio.");
      }

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);

      // Create a new Audio object and play it
      const newAudio = new Audio(audioUrl);
      newAudio.play();
      setAudio(newAudio);
      setIsPlaying(true);

      // Handle when the audio ends
      newAudio.onended = () => {
        setIsPlaying(false);
      };
    } catch (error) {
      console.error("Error playing TTS audio:", error);
    }
  };

  return (
    <div className="game-page">
      <div className="result-card">
        <h1 className="title">Your Results</h1>
        <p className="score">Score: <span>{score}/100</span></p>

        {/* Sentence Section */}
        <h2>Sentence:</h2>
        <div className="sentence-container">
          <p
            className="sentence-text"
            dangerouslySetInnerHTML={{ __html: sentence }} // Render HTML tags
          ></p>
          <button className="speaker-button" onClick={() => playTextToSpeech(sentence)}>
            <img src={SpeakerIcon} alt="Play Sentence" />
          </button>
        </div>

        {/* Feedback Section */}
        <h2>Feedback:</h2>
        <div className="feedback-box">
          <ul className="feedback-list">
            {feedback.split("\n").map((line, index) => (
              <li
                key={index}
                className="feedback-item"
                dangerouslySetInnerHTML={{ __html: line }} // Render HTML for each feedback line
              ></li>
            ))}
          </ul>
          <button className="speaker-button" onClick={() => playTextToSpeech(feedback)}>
            <img src={SpeakerIcon} alt="Play Feedback" />
          </button>
        </div>

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