import { useState } from "react";

export function useTranslation() {
  const [translation, setTranslation] = useState("");
  const [showTranslation, setShowTranslation] = useState(false);

  const fetchTranslation = async (text) => {
    try {
      const response = await fetch("http://localhost:8000/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sentence: text }),
      });
      const data = await response.json();
      setTranslation(data.translation || "");
    } catch {
      setTranslation("Translation unavailable");
    }
  };

  const handleMouseEnter = (sentence) => {
    fetchTranslation(sentence.replace(/<[^>]+>/g, ""));
    setShowTranslation(true);
  };
  const handleMouseLeave = () => setShowTranslation(false);

  return {
    translation,
    showTranslation,
    handleMouseEnter,
    handleMouseLeave,
  };
}