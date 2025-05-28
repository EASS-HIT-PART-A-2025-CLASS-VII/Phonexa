import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./Styling/LevelResult.css";
import SpeakerIcon from "../ProjectImages/speaker.png";
import { useEffect } from "react";
import { useTranslation } from "./useTranslation";
import { useTTS, copyToClipboardAndRedirect } from './useTTS';

const LevelResult = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { score = 0, feedback = "No feedback available.", sentence = "No sentence provided.", audioBlob } = location.state || {};
  const [currentStreak, setCurrentStreak] = useState(
    parseInt(localStorage.getItem("phonexa_current_streak") || "0", 10)
  );
  const { playTextToSpeech, isPlaying, playPhonemeToSpeech, isPhonemeAudioPlaying } = useTTS();

  const {
    translation,
    showTranslation,
    handleMouseEnter,
    handleMouseLeave,
  } = useTranslation();

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

      // Call the LLMTeacher microservice directly
      const response = await fetch("http://localhost:5000/generate-advanced-sentence", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          previous_sentence: cleanSentence,
          feedback: feedback
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const parsedData = await response.json();
      navigate("/level", { state: { sentence: parsedData.sentence, sentence_ipa: parsedData.sentence_ipa } });
    } catch (error) {
      console.error("Error fetching new sentence:", error);
      navigate("/level", { state: { sentence: "Error generating sentence.", sentence_ipa: "Error generating IPA." } });
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
            onClick={() => playPhonemeToSpeech(item.wrong_word)}
            title="Click to hear phonetic pronunciation"
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
        <div className="sentence-container"
          onMouseEnter={() => handleMouseEnter(sentence)}
          onMouseLeave={handleMouseLeave}
          title={showTranslation && translation ? translation : ""} >

          <div
            className="sentence-text"
            dangerouslySetInnerHTML={{ __html: sentence }} // Use the highlighted sentence from LLM
          ></div>
          <button
            className="speaker-button"
            onClick={() => playTextToSpeech(sentence, "right")}
          >
            <img src={SpeakerIcon} alt="Speaker Icon" className="speaker-icon" />
          </button>

        </div>

        {/* Feedback Section */}
        <h2>Suggestions:</h2>
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