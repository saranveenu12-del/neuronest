"""
NeuroNest — Sentiment Analyzer
Analyzes user input for emotional context using keyword-based scoring.
Fully offline — no API required.
"""

# Sentiment lexicon — words mapped to sentiment scores
_POSITIVE_WORDS = {
    "good": 0.6, "great": 0.8, "awesome": 0.9, "amazing": 0.9,
    "wonderful": 0.85, "fantastic": 0.9, "excellent": 0.85,
    "love": 0.8, "like": 0.5, "enjoy": 0.6, "happy": 0.8,
    "glad": 0.7, "excited": 0.8, "beautiful": 0.7, "perfect": 0.9,
    "best": 0.8, "cool": 0.6, "nice": 0.6, "fun": 0.7,
    "brilliant": 0.85, "incredible": 0.85, "thanks": 0.5,
    "thank": 0.5, "please": 0.3, "yes": 0.4, "yeah": 0.4,
    "yep": 0.4, "sure": 0.3, "right": 0.3, "correct": 0.5,
    "interesting": 0.6, "fascinating": 0.7, "impressive": 0.7,
    "helpful": 0.6, "smart": 0.6, "clever": 0.6, "wow": 0.7,
    "superb": 0.85, "outstanding": 0.85, "magnificent": 0.9,
    "delightful": 0.75, "terrific": 0.8, "fabulous": 0.8,
    "bravo": 0.8, "hooray": 0.8, "yay": 0.8, "hurray": 0.8,
}

_NEGATIVE_WORDS = {
    "bad": -0.6, "terrible": -0.9, "awful": -0.85, "horrible": -0.9,
    "hate": -0.8, "dislike": -0.6, "angry": -0.7, "sad": -0.7,
    "upset": -0.6, "annoyed": -0.5, "frustrated": -0.7,
    "boring": -0.5, "stupid": -0.7, "dumb": -0.6, "ugly": -0.6,
    "wrong": -0.5, "no": -0.3, "not": -0.2, "never": -0.4,
    "worst": -0.9, "useless": -0.7, "pathetic": -0.8,
    "disappointing": -0.6, "confused": -0.4, "confusing": -0.5,
    "difficult": -0.3, "hard": -0.2, "impossible": -0.6,
    "fail": -0.6, "failed": -0.6, "failure": -0.7, "sucks": -0.7,
    "broken": -0.5, "ruined": -0.7, "lost": -0.4, "sick": -0.5,
    "tired": -0.4, "bored": -0.5, "lonely": -0.6, "scared": -0.5,
    "afraid": -0.5, "worry": -0.4, "worried": -0.5, "stop": -0.4,
    "shut": -0.5, "bye": -0.2, "goodbye": -0.2,
}

_QUESTION_INDICATORS = {"?", "what", "why", "how", "when", "where", "who", "which", "can", "could", "would", "do", "does", "is", "are"}

_INTENSIFIERS = {"very": 1.3, "really": 1.3, "so": 1.2, "extremely": 1.5, "super": 1.4, "absolutely": 1.4, "totally": 1.3, "incredibly": 1.4, "quite": 1.1}
_NEGATORS = {"not", "no", "never", "neither", "nor", "don't", "doesn't", "didn't", "won't", "wouldn't", "couldn't", "shouldn't", "isn't", "aren't", "wasn't", "weren't", "can't", "cannot"}


class SentimentAnalyzer:
    """Analyzes text for sentiment and emotional signals."""

    def analyze(self, text):
        """
        Analyze text and return sentiment data.

        Returns:
            dict with keys: score (-1 to 1), label, confidence,
                            is_question, detected_emotions
        """
        if not text or not text.strip():
            return self._neutral()

        words = text.lower().split()
        clean_words = [w.strip(".,!?;:'\"()[]") for w in words]

        score = 0.0
        word_scores = []
        is_negated = False

        for i, word in enumerate(clean_words):
            if word in _NEGATORS:
                is_negated = True
                continue

            # Check intensifier
            intensifier = 1.0
            if i > 0 and clean_words[i - 1] in _INTENSIFIERS:
                intensifier = _INTENSIFIERS[clean_words[i - 1]]

            # Score the word
            if word in _POSITIVE_WORDS:
                ws = _POSITIVE_WORDS[word] * intensifier
                if is_negated:
                    ws *= -0.7
                word_scores.append(ws)
                is_negated = False
            elif word in _NEGATIVE_WORDS:
                ws = _NEGATIVE_WORDS[word] * intensifier
                if is_negated:
                    ws *= -0.5
                word_scores.append(ws)
                is_negated = False
            else:
                is_negated = False

        # Compute average score
        if word_scores:
            score = sum(word_scores) / len(word_scores)
            # Boost slightly if many sentiment words
            if len(word_scores) > 3:
                score *= 1.1

        score = max(-1.0, min(1.0, score))

        # Determine label
        if score > 0.3:
            label = "positive"
        elif score > 0.1:
            label = "slightly_positive"
        elif score < -0.3:
            label = "negative"
        elif score < -0.1:
            label = "slightly_negative"
        else:
            label = "neutral"

        # Check if question
        is_question = "?" in text or (
            len(clean_words) > 0 and clean_words[0] in _QUESTION_INDICATORS
        )

        # Detect specific emotions
        emotions = self._detect_emotions(clean_words, score, is_question)

        # Confidence based on how many sentiment words we found
        confidence = min(1.0, len(word_scores) * 0.2 + 0.3) if word_scores else 0.3

        return {
            "score": round(score, 3),
            "label": label,
            "confidence": round(confidence, 2),
            "is_question": is_question,
            "detected_emotions": emotions,
            "word_count": len(clean_words),
        }

    def _neutral(self):
        return {
            "score": 0.0, "label": "neutral", "confidence": 0.5,
            "is_question": False, "detected_emotions": ["calm"],
            "word_count": 0,
        }

    def _detect_emotions(self, words, score, is_question):
        """Detect specific emotions from word patterns."""
        emotions = []
        word_set = set(words)

        # Excitement / joy
        joy_words = {"happy", "excited", "love", "amazing", "awesome", "wow", "yay", "great", "wonderful", "fantastic"}
        if word_set & joy_words:
            emotions.append("joy")

        # Curiosity
        if is_question or word_set & {"curious", "wonder", "interesting", "fascinating", "how", "why"}:
            emotions.append("curiosity")

        # Frustration / anger
        if word_set & {"frustrated", "angry", "annoyed", "hate", "stupid", "ugh"}:
            emotions.append("frustration")

        # Sadness
        if word_set & {"sad", "lonely", "miss", "lost", "depressed", "unhappy", "crying"}:
            emotions.append("sadness")

        # Confusion
        if word_set & {"confused", "confusing", "understand", "what", "huh"} and is_question:
            emotions.append("confusion")

        # Gratitude
        if word_set & {"thanks", "thank", "appreciate", "grateful"}:
            emotions.append("gratitude")

        # Fear / worry
        if word_set & {"scared", "afraid", "worried", "worry", "fear", "nervous"}:
            emotions.append("concern")

        if not emotions:
            if score > 0.2:
                emotions.append("positive")
            elif score < -0.2:
                emotions.append("negative")
            else:
                emotions.append("calm")

        return emotions
