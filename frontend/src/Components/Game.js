import React, { useState, useRef } from "react";
import { useLocation } from "react-router-dom";
import PlayPauseButton from "../ProjectImages/playpausebtn.png";
import "./Styling/Game.css"; // Reuse StartPage.css for consistent styling

const Game = () => {
  const location = useLocation();
  const sentence = location.state?.sentence || "No sentence provided.";
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [recordingStatus, setRecordingStatus] = useState(""); // Recording status text
  const mediaRecorderRef = useRef(null); // Reference to the MediaRecorder instance

  // Function to handle recording
  const toggleRecording = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert("Your browser does not support audio recording.");
      return;
    }

    if (isRecording) {
      // Stop recording immediately
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
      setRecordingStatus("Recording stopped.");
    } else {
      // Start recording
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        const chunks = [];

        mediaRecorder.ondataavailable = (event) => {
          chunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
          const blob = new Blob(chunks, { type: "audio/wav" });
          setAudioBlob(blob); // Update the audio blob
          setRecordingStatus("Recording stopped.");
        };

        mediaRecorder.start();
        mediaRecorderRef.current = mediaRecorder; // Store the MediaRecorder instance
        setIsRecording(true);
        setRecordingStatus("Recording...");

        setTimeout(() => {
          if (mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
            setIsRecording(false);
            setRecordingStatus("Recording stopped.");
          }
        }, 20000); // Stop recording after 20 seconds
      } catch (error) {
        console.error("Error starting recording:", error);
      }
    }
  };

  // Function to upload the sentence and audio to the backend
  const uploadData = async () => {
    if (!audioBlob || !sentence) {
      alert("Please record audio first.");
      return;
    }

    const formData = new FormData();
    formData.append("sentence", sentence);
    formData.append("audio", audioBlob, "recording.wav");

    try {
      const response = await fetch("http://localhost:8000/analysis", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        console.log("Response received from backend.");
      } else {
        console.error("Failed to upload data.");
      }
    } catch (error) {
      console.error("Error uploading data:", error);
    }
  };

  return (
    <div className="game-page">
      <h1 className="title">Pronunciation Game</h1>
      <p className="instructions">Read the following sentence:</p>
      <div className="sentence-box">
        <h2 className="sentence-text">{sentence}</h2>
      </div>
  
      {/* Recording Container */}
      <div className="recording-container">
        {audioBlob && (
          <audio
            controls
            src={URL.createObjectURL(audioBlob)}
            className="audio-player"
          >
            Your browser does not support the audio element.
          </audio>
        )}
        <p className="recording-status">{recordingStatus}</p>
      </div>
  
      {/* Record Button */}
      <button
        onClick={toggleRecording}
        className={`record-button ${isRecording ? "recording" : ""}`}
      >
        <img
          src={PlayPauseButton}
          alt={isRecording ? "Stop Recording" : "Start Recording"}
          className="record-button-img"
        />
      </button>
  
      {/* Submit Button */}
      <button
        className="submit-button"
        onClick={uploadData}
        disabled={!audioBlob}
      >
        Submit
      </button>
    </div>
  );
};

export default Game;