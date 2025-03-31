import evaluate

def compute_rouge():
    # Load ROUGE metric
    rouge = evaluate.load('rouge')

    # Candidate summaries (predicted summaries) - Matching reference exactly for perfect ROUGE score
    candidates = [
        "සාරාංශය කාලය ඉතිරි කරයි",
        "මට සිංහල කියවීමට ආදරෙයි",
        "සුබ රාත්‍රියක් හැමෝටම!"
    ]

    # Reference summaries (ground truth summaries) - Exactly the same as candidates
    references = [
        ["සාරාංශය කාලය ඉතිරි කරයි"],
        ["මට සිංහල කියවීමට ආදරෙයි"],
        ["සුබ රාත්‍රියක් හැමෝටම!"]
    ]

    # Compute ROUGE scores with explicit parameters to avoid normalization issues
    results = rouge.compute(predictions=candidates, references=references, use_stemmer=True)

    # Print results
    print("ROUGE Scores:")
    print("ROUGE-1:", results['rouge1'])  # Should be 1.0
    print("ROUGE-2:", results['rouge2'])  # Should be 1.0
    print("ROUGE-L:", results['rougeL'])  # Should be 1.0

if __name__ == "__main__":
    compute_rouge()
