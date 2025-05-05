import { useState } from "react";

export function useTTS() {
  const [audio, setAudio] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const playTextToSpeech = async (text) => {
    if (isPlaying && audio) {
      audio.pause();
      audio.currentTime = 0;
      setIsPlaying(false);
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sentence: text }),
      });

      if (!response.ok) throw new Error("Failed to fetch TTS audio.");

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);

      const newAudio = new Audio(audioUrl);
      newAudio.play();
      setAudio(newAudio);
      setIsPlaying(true);

      newAudio.onended = () => setIsPlaying(false);
    } catch (error) {
      console.error("Error playing TTS audio:", error);
    }
  };

  return { playTextToSpeech, isPlaying };
}

export function copyToClipboardAndRedirect(text) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text);
  } else {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  }
  window.open("https://ipa-reader.com/", "_blank");
}