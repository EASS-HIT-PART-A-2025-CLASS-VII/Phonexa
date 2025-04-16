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
          Authorization: `Bearer ${process.env.REACT_APP_API_KEY}`,
        },
        body: JSON.stringify({
          model: "mistral-small-latest",
          messages: [
        { role: "system", content: "You are aמ English sentence generating machine that provides a JSON object containing a sentence and its IPA (International Phonetic Alphabet) representation with spaces. Ensure the response is a valid JSON object without any additional symbols or formatting." },
        { role: "user", content: "Generate a random basic sentence for pronunciation evaluation and its IPA representation. Ensure the response is a valid JSON object without any irrelevant symbols or formatting, ensure the json field names are sentence and sentence_ipa" },
          ],
          temperature: 0.7,
          max_tokens: 100,
          top_p: 1.0,
          stream: false,
        }),
      });
  
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
  
      const data = await response.json();
      const generatedSentence = data.choices?.[0]?.message?.content || '{"sentence": "Error generating sentence.", "sentence_ipa": "Error generating IPA."}';
      const parsedData = JSON.parse(generatedSentence);
  
      navigate("/level", { state: { sentence: parsedData.sentence, sentence_ipa: parsedData.sentence_ipa } });
    } catch (error) {
      console.error("Error fetching sentence:", error);
  
      // Navigate to the level page with error state
      navigate("/level", { state: { sentence: "Error generating sentence.", sentence_ipa: "Error generating IPA." } });
    }
  };

  return (
    <div className="start-page">
      <div className="start-card">
        <img src={PhonexaLogo} alt="Phonexa Logo" className="logo" />
        <h1 className="title">Phonexa</h1>
        <h2 className="subtitle">A.I Pronunciation Game</h2>
        <p className="score">Highest Score: 0</p>

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