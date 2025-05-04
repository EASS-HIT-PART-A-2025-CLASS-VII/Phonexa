import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./Styling/LevelResult.css";
import SpeakerIcon from "../ProjectImages/speaker.png";
import { useEffect } from "react";
import { getNextLevelSentence } from './NextLevel';

const LevelResult = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { score = 0, feedback = "No feedback available.", sentence = "No sentence provided.", audioBlob } = location.state || {};
  const [audio, setAudio] = useState(null); // State to manage the audio object
  const [isPlaying, setIsPlaying] = useState(false); // State to track if audio is playing
  const [currentStreak, setCurrentStreak] = useState(
    parseInt(localStorage.getItem("phonexa_current_streak") || "0", 10)
  );

  useEffect(() => {
    setCurrentStreak(parseInt(localStorage.getItem("phonexa_current_streak") || "0", 10));
  }, []);


  // Function to retry the level
  const retryLevel = () => {
    // Navigate back to the previous page in history
    navigate(-1);
  };

  // Function to fetch a new sentence for the next level
  const fetchNextLevel = async () => {
    try {
      // Clean the sentence from any HTML tags
      const cleanSentence = sentence.replace(/<[^>]+>/g, "");
      const parsedData = await getNextLevelSentence(cleanSentence, feedback);
      navigate("/level", { state: { sentence: parsedData.sentence, sentence_ipa: parsedData.sentence_ipa } });
    } catch (error) {
      console.error("Error fetching new sentence:", error);
    }
  };

  const copyToClipboardAndRedirect = (text) => {
    // Copy to clipboard
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text);
    } else {
      // Fallback for older browsers
      const textarea = document.createElement("textarea");
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
    }
    // Redirect to ipa-reader.com
    window.open("https://ipa-reader.com/", "_blank");
  };
  
  const playTextToSpeech = async (text, type = "right") => {
    if (type === "wrong") {
      copyToClipboardAndRedirect(text);
      return;
    }
  
    if (isPlaying && audio) {
      audio.pause();
      audio.currentTime = 0;
      setIsPlaying(false);
      return;
    }
  
    try {
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
  
      const newAudio = new Audio(audioUrl);
      newAudio.play();
      setAudio(newAudio);
      setIsPlaying(true);
  
      newAudio.onended = () => {
        setIsPlaying(false);
      };
    } catch (error) {
      console.error("Error playing TTS audio:", error);
    }
  };
  
  const renderFeedbackLine = (item, index) => {
    if (typeof item === 'string' && item === "PERFECT!") {
      return <span className="feedback-text perfect">{item}</span>;
    }
    if (typeof item === 'object' && item.right_word && item.wrong_word) {
      return (
        <span className="feedback-text">
          Try saying{' '}
          <button
        className="word-button green"
        onClick={() => playTextToSpeech(item.en_word, "right")}
        title={item.en_word}
          >{item.right_word}</button>{' '}
          instead of{' '}
          <button
        className="word-button red"
        onClick={() => playTextToSpeech(item.wrong_word, "wrong")}
          >{item.wrong_word}</button>.
        </span>
      );
    }
    return <span className="feedback-text error">Invalid feedback format</span>;
  };



  return (
    <div className="game-page">
      <div className="result-card">
        <div className="current-streak">Streak: {currentStreak}</div>
        <h1 className="title">Your Results</h1>
        <p className="score">Score: <span>{score}/100</span></p>

        {/* Sentence Section - Highlighted sentence from LLM */}
        <h2>Sentence:</h2>
        <div className="sentence-container">
          <p
            className="sentence-text"
            dangerouslySetInnerHTML={{ __html: sentence }} // Use the highlighted sentence from LLM
          ></p>
          <button
            className="speaker-button"
            onClick={() => playTextToSpeech(sentence, "right")}
          >
            <img src={SpeakerIcon} alt="Speaker Icon" className="speaker-icon" />
          </button>
          
        </div>

        {/* Feedback Section */}
        <h2>Feedback:</h2>
        <div className="feedback-box">
          <ul className="feedback-list">
            {/* Check if feedback is an array before mapping */}
            {Array.isArray(feedback) ? (
              feedback.map((item, index) => (
                <li key={index} className="feedback-item">
                  {renderFeedbackLine(item, index)}
                  
                </li>
              ))
            ) : (
              // Handle case where feedback might not be an array (e.g., initial state or error)
              <li className="feedback-item">
                <span className="feedback-text">{typeof feedback === 'string' ? feedback : "Feedback data is invalid."}</span>
              </li>
            )}
          </ul>
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
          <button className="next-button" onClick={fetchNextLevel}>
            Next Level
          </button>
        </div>
      </div>
    </div>
  );
};

export default LevelResult;