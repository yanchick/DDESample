import loguru
from flows import arxiv_analysis_flow
from datetime import datetime
import argparse
from pathlib import Path

# Настройка логирования
logger = loguru.logger


def setup_folders():
    """Создание необходимых папок для проекта"""
    folders = ['logs', 'eda_results', 'data']
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)


def run_pipeline(max_papers: int = 100, save_results: bool = True):
    """
    Запуск пайплайна обработки данных

    Args:
        max_papers (int): Максимальное количество статей для сбора
        save_results (bool): Сохранять ли результаты анализа
    """
    try:
        logger.info("Starting the ArXiv papers analysis pipeline")
        start_time = datetime.now()

        # Запуск flow
        results = arxiv_analysis_flow(max_papers=max_papers)

        # Логирование результатов
        execution_time = datetime.now() - start_time
        logger.info(f"Pipeline completed successfully in {execution_time}")
        logger.info("Summary of results:")
        logger.info(f"Total papers processed: {results.get('total_papers', 0)}")
        logger.info(f"Unique authors found: {results.get('unique_authors', 0)}")
        logger.info(f"Date range: {results.get('date_range', 'N/A')}")

        return results

    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}")
        raise


def main():
    """Основная функция запуска программы"""
    parser = argparse.ArgumentParser(description='ArXiv Papers Analysis Pipeline')
    parser.add_argument(
        '--max-papers',
        type=int,
        default=100,
        help='Maximum number of papers to collect (default: 100)'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results to disk'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    # Настройка уровня логирования
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Создание необходимых папок
    setup_folders()

    logger.info("=== ArXiv Papers Analysis Pipeline ===")
    logger.info(f"Max papers to collect: {args.max_papers}")
    logger.info(f"Save results: {not args.no_save}")

    try:
        # Запуск пайплайна
        results = run_pipeline(
            max_papers=args.max_papers,
            save_results=not args.no_save
        )

        # Вывод итоговой информации
        print("\n=== Pipeline Execution Summary ===")
        print(f"Total papers processed: {results.get('total_papers', 0)}")
        print(f"Unique authors: {results.get('unique_authors', 0)}")
        print(f"Date range: {results.get('date_range', 'N/A')}")
        print("\nResults have been saved to:")
        print("- Database: arxiv_papers.db")
        print("- Visualizations: ./eda_results/")
        print("\nPipeline completed successfully!")

    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        print("\nPipeline interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        print(f"\nPipeline failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
