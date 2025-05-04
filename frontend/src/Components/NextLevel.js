const ANIMAL_LIST = [
    "cat", "dog", "elephant", "lion", "tiger", "bear", "giraffe", "zebra", "monkey", "kangaroo",
    "panda", "wolf", "fox", "rabbit", "deer", "hippopotamus", "rhinoceros", "leopard", "cheetah",
    "crocodile", "alligator", "bat", "otter", "squirrel", "hedgehog", "moose", "buffalo", "bison",
    "goat", "sheep", "cow", "horse", "donkey", "pig", "chicken", "duck", "goose", "turkey", "owl",
    "eagle", "falcon", "parrot", "penguin", "seal", "walrus", "dolphin", "whale", "shark", "octopus",
    "antelope", "armadillo", "badger", "beaver", "camel", "chimpanzee", "cougar", "crab", "crow", "dingo",
    "dragonfly", "ferret", "flamingo", "gazelle", "gorilla", "hamster", "hyena", "ibis", "jackal", "jaguar",
    "lemur", "llama", "lobster", "lynx", "mole", "mongoose", "narwhal", "newt", "opossum", "orangutan",
    "ostrich", "panther", "peacock", "pelican", "platypus", "porcupine", "quail", "raccoon", "rat", "reindeer",
    "salamander", "scorpion", "seal", "skunk", "sloth", "snail", "snake", "sparrow", "swan", "tapir",
    "termite", "toad", "tortoise", "vulture", "weasel", "wombat", "woodpecker", "yak", "lemur", "gazelle"
];
  
  function extractAnimals(sentence) {
    // Simple regex-based extraction (case-insensitive, word boundaries)
    const animalsFound = [];
    for (const animal of ANIMAL_LIST) {
      const regex = new RegExp(`\\b${animal}\\b`, "i");
      if (regex.test(sentence)) animalsFound.push(animal);
    }
    return animalsFound;
  }
  
  export const getNextLevelSentence = async (sentence, feedback) => {
    // 1. Get used animals from localStorage
    let usedAnimals = [];
    try {
      usedAnimals = JSON.parse(localStorage.getItem("phonexa_used_animals") || "[]");
    } catch {
      usedAnimals = [];
    }
  
    // 2. Extract animals from the current sentence and update usedAnimals
    const animalsInSentence = extractAnimals(sentence);
    const updatedUsedAnimals = Array.from(new Set([...usedAnimals, ...animalsInSentence]));
    localStorage.setItem("phonexa_used_animals", JSON.stringify(updatedUsedAnimals));
  
    // 3. Filter available animals
    const availableAnimals = ANIMAL_LIST.filter(animal => !updatedUsedAnimals.includes(animal));
    const animalListString = availableAnimals.join(", ");
  
    // 4. Build prompt
    const userPrompt = `
  You are an English sentence generating machine for a pronunciation game. 
  Your task is to generate the next sentence for the user to pronounce, and the sentence must be themed around animals.
  Instructions:
  1. Only use animals from this list: [${animalListString}].
  2. Do NOT use any animal that appears in this list of already used animals: [${updatedUsedAnimals.join(", ")}].
  3. If the 'Feedback' is exactly "PERFECT!" or contains only "PERFECT!", generate a new animal-themed sentence that is generally slightly more difficult in terms of pronunciation than the 'Previous Sentence'.
  4. If the 'Feedback' contains specific pronunciation advice (e.g., "Try saying X instead of Y"), generate a new animal-themed sentence that specifically includes sounds related to those difficulties to help the user practice.
  5. Do NOT reuse the previous sentence's structure, vocabulary, or theme. The new sentence must be unique and introduce new words or patterns.
  6. Your response MUST be a valid JSON object containing only two keys: 'sentence' (the new sentence string) and 'sentence_ipa' (the full IPA transcription of the new sentence with spaces between words). Do not include any other text, explanations, or formatting outside the JSON object.
  Previous Sentence: "${sentence}"
  Feedback: "${feedback}"
  `;
  
    // 5. Call the LLM API as before
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
            { role: "system", content: "You are an English sentence generating machine that provides a JSON object containing a sentence and its IPA (International Phonetic Alphabet) representation with spaces. Ensure the response is a valid JSON object without any additional symbols or formatting." },
            { role: "user", content: userPrompt },
          ],
          temperature: 0.9,
          max_tokens: 120,
          top_p: 1.0,
          stream: false,
        }),
      });
  
      if (response.ok) {
        const data = await response.json();
        const newSentence = data.choices?.[0]?.message?.content || "Error generating sentence.";
        const parsedData = JSON.parse(newSentence);
        return parsedData;
      } else {
        throw new Error("Failed to fetch new sentence.");
      }
    } catch (error) {
      console.error("Error fetching new sentence:", error);
      throw error;
    }
  };