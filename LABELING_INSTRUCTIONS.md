# Manual Tweet Labeling Instructions

## Purpose
Label tweets with sentiment scores to validate our automated sentiment analysis model (twitter-roberta + finance keywords).

---

## How to Label

### 1. **manual_sentiment_score** (Required)
Rate the tweet's sentiment on a scale from **-1.0 to +1.0**:

- **-1.0 to -0.5**: **Strongly Bearish** 
  - Example: "Market crash incoming", "Nifty breakdown", "sell everything"
  
- **-0.5 to -0.1**: **Mildly Bearish**
  - Example: "Resistance ahead", "caution advised", "profit booking expected"
  
- **-0.1 to +0.1**: **Neutral**
  - Example: News updates, factual statements, promotional content without bias
  
- **+0.1 to +0.5**: **Mildly Bullish**
  - Example: "Good support level", "potential upside", "watch this stock"
  
- **+0.5 to +1.0**: **Strongly Bullish**
  - Example: "Breakout confirmed!", "Strong rally", "Buy the dip", "massive profit"

### 2. **manual_sentiment_label** (Required)
Choose one:
- `BEARISH` (score < -0.1)
- `NEUTRAL` (score between -0.1 and +0.1)
- `BULLISH` (score > +0.1)

### 3. **confidence** (Required)
How confident are you in your label?
- `HIGH`: Clear sentiment, easy to interpret
- `MEDIUM`: Some ambiguity but leaning one way
- `LOW`: Very unclear, promotional spam, or contradictory signals

### 4. **notes** (Optional)
Add any comments:
- Why you chose this sentiment
- Specific keywords that influenced your decision
- Any ambiguity or special considerations

---

## Special Cases

### **Promotional/Spam Tweets**
(e.g., "Join my Telegram", "Get free tips")
- **Score:** 0.0 (neutral)
- **Label:** NEUTRAL
- **Confidence:** LOW
- **Notes:** "Promotional content - no market sentiment"

### **Factual News**
(e.g., "NSE revises lot sizes", "Bank reported 17% increase")
- **Score:** 0.0 to +0.2 (slightly positive if it's good news)
- **Label:** NEUTRAL or BULLISH (depending on news)
- **Confidence:** MEDIUM to HIGH

### **Profit Updates**
(e.g., "Profit of Rs 63k")
- **Score:** +0.3 to +0.7 (bullish - successful trades inspire confidence)
- **Label:** BULLISH
- **Confidence:** MEDIUM to HIGH

### **Multiple Sentiments in One Tweet**
(e.g., "HAL hit target, but TATA hit stop-loss")
- Score based on **overall net sentiment**
- Lower confidence due to mixed signals

---

## Example Labels

### Example 1:
**Tweet:** "Position update on nifty Profit of rs 63k"
- **Score:** +0.6
- **Label:** BULLISH
- **Confidence:** HIGH
- **Notes:** "Clear profit announcement - bullish signal"

### Example 2:
**Tweet:** "Join Here https://telegram.im/InsightServices"
- **Score:** 0.0
- **Label:** NEUTRAL
- **Confidence:** LOW
- **Notes:** "Pure spam/promotional - no market sentiment"

### Example 3:
**Tweet:** "3.10.25: US govt shut, RBI changes the mood for the bulls before Diwali"
- **Score:** +0.3
- **Label:** BULLISH
- **Confidence:** MEDIUM
- **Notes:** "Mixed news but 'mood for bulls' suggests positive sentiment"

### Example 4:
**Tweet:** "NSE revises lot sizes for index derivatives effective Oct 28, 2025"
- **Score:** 0.0
- **Label:** NEUTRAL
- **Confidence:** HIGH
- **Notes:** "Factual regulatory update - no sentiment"

---

## Tips for Consistency

1. **Focus on market sentiment**, not personal opinion
2. **Consider the author's intent** - are they bullish, bearish, or just sharing info?
3. **Keywords matter:**
   - Bullish: profit, breakout, rally, support, buy, calls, target hit
   - Bearish: loss, breakdown, resistance, sell, puts, stop-loss hit
4. **Ignore promotional noise** - focus on the actual market signal
5. **When in doubt**, go with NEUTRAL and MEDIUM/LOW confidence

---

## After Labeling

Save the file as `manual_labels.csv` and we'll use it to:
1. Test our sentiment model's accuracy
2. Identify where the model needs improvement
3. Fine-tune finance keyword weights

---

**Ready to start labeling!** 🎯

Open `manual_labels_template.csv`, fill in your labels, and save as `manual_labels.csv`.
