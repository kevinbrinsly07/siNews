from transformers import TFMT5ForConditionalGeneration, T5Tokenizer
import tensorflow as tf
import os
import re
from summa import summarizer 
from nltk.tokenize import sent_tokenize
# Set TensorFlow seed to remove warnings related to unseeded initializers
tf.keras.utils.set_random_seed(42)

class Summarizer:
    def __init__(self, model_path="kbrinsly7/mt5-sinhala-news-finetunedV3"):
        self.model, self.tokenizer = self.load_model(model_path)

    def load_model(self, model_path):
        try:
            print(f"Loading TensorFlow model from: {model_path}")
            model = TFMT5ForConditionalGeneration.from_pretrained(model_path)
            tokenizer = T5Tokenizer.from_pretrained(model_path)
            print("Model and tokenizer loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e
        return model, tokenizer
    
    def remove_repeated_phrases(self, text):
        """Remove repeated words or phrases from the text."""
        pattern = r'\b(\w+(?:\s+\w+)*)\b(?=\s+\1\b)'
        cleaned_text = re.sub(pattern, r'\1', text, flags=re.IGNORECASE)
        return cleaned_text

    def generate_summary_from_mt5(self, text):
        try:
          
            # print(f"Generating summary for text: {text[:100]}...")  
            # Tokenize input text for summarization
            inputs = self.tokenizer(
                "summarize: " + text, 
                return_tensors="tf", 
                max_length=512, 
                truncation=True
            )
            
            print("Text tokenized successfully. Tokenized input:", inputs["input_ids"][:5]) 
            
            # Generate summary using the pre-trained model
            summary_ids = self.model.generate(
                inputs["input_ids"],
                max_length=512,
                min_length=5,
                num_beams=5,
                early_stopping=True,
                repetition_penalty=1.2, 
                temperature=0.7,  # Encourage diverse outputs
                top_k=50,  # Enable top-k sampling
                top_p=0.9  # Enable nucleus sampling
            )
            
            print(f"Summary generation completed. Output IDs: {summary_ids[0][:5]}")
            
            # Decode the generated summary
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            print(f"Generated summary: {summary[:200]}...")
            # Remove repeated phrases
            # summary = self.remove_repeated_phrases(summary)
            
        except Exception as e:
          
            print(f"Error generating abstractive summary: {e}")
            summary = "Abstractive summary could not be generated."
            
        return summary
    
    # def generate_extractive_summary(self, text):
    #     try:
    #         # Generate extractive summary using summa library
    #         extractive_summary = summarizer.summarize(text)
    #         if not extractive_summary:
    #             extractive_summary = "No extractive summary could be generated."
    #     except Exception as e:
    #         print(f"Error generating extractive summary: {e}")
    #         extractive_summary = "Extractive summary could not be generated."
            
    #     print()
    #     return extractive_summary
    


    def generate_extractive_summary(self, text, num_sentences=3):
        try:
            sentences = sent_tokenize(text)  # Tokenize text into sentences
            if len(sentences) > num_sentences:
                extractive_summary = " ".join(sentences[-num_sentences:])  # Get the last `num_sentences`
                extractive_summary = summarizer.summarize(text)
            else:
                extractive_summary = text  # If text is short, return as-is
                extractive_summary = summarizer.summarize(text)
        except Exception as e:
            print(f"Error generating extractive summary: {e}")
            extractive_summary = "Extractive summary could not be generated."
        
        return extractive_summary


    def summarize_article(self, article):
     # Extractive summary
     extractive_summary = self.generate_extractive_summary(article)
     
     # Abstractive summary
     abstractive_summary = self.generate_summary_from_mt5(article)
    
     # Combine both summaries into one paragraph
     combined_summary = abstractive_summary + " " + extractive_summary
    #  combined_summary = abstractive_summary 
    
    
     return combined_summary


