import React, { useState, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import PlayPauseButton from "../ProjectImages/playpausebtn.png";
import "./Styling/Level.css";

const Level = () => {
  const location = useLocation();
  const sentence = location.state?.sentence || "No sentence provided.";
  const sentenceIPA = location.state?.sentence_ipa || "No IPA provided.";
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [recordingStatus, setRecordingStatus] = useState("");
  const mediaRecorderRef = useRef(null);
  const navigate = useNavigate();

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
    if (!audioBlob || !sentence) {
      alert("Please record audio first.");
      return;
    }

    const formData = new FormData();
    formData.append("sentence", sentence);
    formData.append ("sentenceIPA", sentenceIPA)
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
        const feedback = parsedContent.try_saying.join("\n"); // Combine feedback lines into one string
        const sentence = parsedContent.highlighted_sentence.replace(/\\/g, ""); // Remove redundant slashes
  
        // Navigate to the next page with the processed data
        navigate("/level-result", {
          state: {
            canAccess: true,
            score: score,
            feedback: feedback,
            sentence: sentence,
            audioBlob,
          },
        });
      } else {
        console.error("Failed to upload data.");
      }
    } catch (error) {
      console.error("Error uploading data:", error);
    }
  };

  return (
    <div className="game-page">
      <div className="level-card">
        <h1 className="title">Pronunciation Game</h1>
        <p className="instructions">Read the following sentence:</p>
        <div className="sentence-box">
          <h2 className="sentence-text" dangerouslySetInnerHTML={{ __html: sentence }}></h2>
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
  
          <button className="submit-button" onClick={uploadData} disabled={!audioBlob}>
            Submit
          </button>
        </div>
      </div>
    </div>
  );
};

export default Level;