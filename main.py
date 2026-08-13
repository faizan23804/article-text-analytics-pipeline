
from article_text_analysis.src.pipeline import run_full_pipeline

if __name__ == "__main__":
    result = run_full_pipeline()

    print("\n PIPELINE RUN COMPLETE. ")
    print(f"Total URLs:   {result['total']}")
    print(f"Succeeded:    {result['success_count']}")
    print(f"Failed:       {result['failed_count']}")
    if result["failed_ids"]:
        print(f"Failed IDs:   {result['failed_ids']}")
    print(f"Output saved: {result['output_path']}")