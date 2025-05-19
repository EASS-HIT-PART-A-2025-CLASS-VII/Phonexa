import React, { useState, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import PlayPauseButton from "../ProjectImages/playpausebtn.png";
import "./Styling/Level.css";
import { useEffect } from "react";
import { useTranslation } from "./useTranslation";
import { useTTS } from './useTTS';
import SpeakerIcon from "../ProjectImages/speaker.png";



const Level = () => {
  const location = useLocation();
  const sentence = location.state?.sentence || "No sentence provided.";
  const sentenceIPA = location.state?.sentence_ipa || "No IPA provided.";
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [recordingStatus, setRecordingStatus] = useState("");
  const mediaRecorderRef = useRef(null);
  const navigate = useNavigate();
  const [currentStreak, setCurrentStreak] = useState(
    parseInt(localStorage.getItem("phonexa_current_streak") || "0", 10)
  );
  const { playTextToSpeech, isPlaying } = useTTS();

  const {
    translation,
    showTranslation,
    handleMouseEnter,
    handleMouseLeave,
  } = useTranslation();

  useEffect(() => {
    setCurrentStreak(parseInt(localStorage.getItem("phonexa_current_streak") || "0", 10));
  }, []);


  const toggleRecording = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert("Your browser does not support audio recording.");
      return;
    }

    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
      setRecordingStatus("Recording stopped.");
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        const chunks = [];

        mediaRecorder.ondataavailable = (event) => {
          chunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
          const blob = new Blob(chunks, { type: "audio/wav" });
          setAudioBlob(blob);
          setRecordingStatus("Recording stopped.");
        };

        mediaRecorder.start();
        mediaRecorderRef.current = mediaRecorder;
        setIsRecording(true);
        setRecordingStatus("Recording...");

        setTimeout(() => {
          if (mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
            setIsRecording(false);
            setRecordingStatus("Recording stopped.");
          }
        }, 20000);
      } catch (error) {
        console.error("Error starting recording:", error);
      }
    }
  };

  const uploadData = async () => {
    setLoading(true);
    if (!audioBlob || !sentence) {
      alert("Please record audio first.");
      return;
    }

    localStorage.setItem("phonexa_current_streak", (currentStreak + 1).toString());

    const formData = new FormData();
    formData.append("sentence", sentence);
    formData.append("sentenceIPA", sentenceIPA)
    formData.append("audio", audioBlob, "recording.wav");

    try {
      const response = await fetch("http://localhost:8000/analysis", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();

        // Extract the content from the LLM response
        const contentString = data.choices?.[0]?.message?.content;
        if (!contentString) {
          throw new Error("Invalid response format: Missing 'content' attribute.");
        }

        // Parse the content string into a JSON object
        const parsedContent = JSON.parse(contentString);

        // Extract and process the response content
        const score = parsedContent.score;
        const feedback = parsedContent.try_saying
        const sentence = parsedContent.highlighted_sentence.replace(/\\/g, ""); // Remove redundant slashes

        // Navigate to the next page with the processed data
        navigate("/level-result", {
          state: {
            canAccess: true,
            score: score,
            feedback: feedback,
            sentence: sentence,
            audioBlob
          },
        });
      } else {
        console.error("Failed to upload data.");
      }
    } catch (error) {
      console.error("Error uploading data:", error);
    } finally {
      setLoading(false);
    }
  };




  return (
    <div className="game-page">
      <div className="level-card">
        <div className="current-streak">Streak: {currentStreak}</div>
        <h1 className="title">Pronunciation Game</h1>
        <p className="instructions">Read the following sentence:</p>
        <div
          className="sentence-box"
          onMouseEnter={() => handleMouseEnter(sentence)}
          onMouseLeave={handleMouseLeave}
          title={showTranslation && translation ? translation : ""}
        >
          <div className="sentence-text" dangerouslySetInnerHTML={{ __html: sentence }}></div>
          <button
            className="speaker-button"
            onClick={() => playTextToSpeech(sentence)}

          >
            <img src={SpeakerIcon} alt="Speaker Icon" className="speaker-icon" />
          </button>
        </div>

        <div className="recording-container">
          <h2 className="recording-title">Your Attempt</h2>
          <div className="recording-placeholder">
            {audioBlob ? (
              <audio controls src={URL.createObjectURL(audioBlob)} className="audio-player">
                Your browser does not support the audio element.
              </audio>
            ) : (
              <p>No audio available.</p>
            )}
          </div>
          <p className="recording-status">{recordingStatus}</p>
        </div>

        {/* Button Container */}
        <div className="button-container">
          <button onClick={toggleRecording} className={`record-button ${isRecording ? "recording" : ""}`}>
            <img src={PlayPauseButton} alt={isRecording ? "Stop Recording" : "Start Recording"} className="record-button-img" />
          </button>

          <button className="submit-button" onClick={uploadData} disabled={!audioBlob || loading}>
            Submit
          </button>
          {loading && (
            <span className="inline-spinner">
              <span className="spinner"></span>
              Processing...
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default Level;