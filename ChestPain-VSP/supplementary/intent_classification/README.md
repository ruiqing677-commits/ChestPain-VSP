# Intent Classification Supplement

This folder provides supplementary materials for the chest-pain-specific intent classification evaluation used in ChestPain-VSP.

The prompt-based intent classifier maps user utterances to predefined clinical intent categories. These intent categories support controlled disclosure, triggered diagnostic evidence, and CPRG-based process evaluation.

## Reported Performance

- Accuracy: 92.86%
- Macro-F1: 93.40%

All precision, recall, F1, and accuracy values are reported as percentages. Support values are omitted for compact presentation.

## Included Files

- `intent_label_definitions.md`: definitions of the intent categories used by ChestPain-VSP.
- `category_level_results.csv`: category-level precision, recall, and F1 results.
- `intent_examples.md`: representative utterance examples for each intent category.

## Notes

The intent label definitions, category-level results, and representative examples were manually reviewed for consistency, clarity, and relevance to chest pain consultation. Representative examples are de-identified and do not contain patient-level clinical records or personal identifiers.
