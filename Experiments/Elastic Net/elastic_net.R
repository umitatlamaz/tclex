library(tidyverse)
library(caret)
library(glmnet)


file_path <- '../TCLex-AoA.tsv'
df <- read_tsv(file_path)
df <- df %>%
  mutate(clc_normalized = parse_number(clc_normalized))

#Calculate Zipf values (zeros are marked as NA)
df <- df %>%
  mutate(
    tclex_zipf  = ifelse(tclex_normalized > 0, log10(tclex_normalized) + 3, NA),
    clc_zipf    = ifelse(clc_normalized      > 0, log10(clc_normalized)      + 3, NA),
    tekcan_zipf = ifelse(tekcan_frequency    > 0, log10(tekcan_frequency)    + 3, NA)
  )

cat("--- Zero/NA Check After Transformation ---\n")
df %>%
  summarise(
    tclex_na  = sum(is.na(tclex_zipf)),
    clc_na    = sum(is.na(clc_zipf)),
    tekcan_na = sum(is.na(tekcan_zipf)),
    n_total   = n()
  ) %>%
  print()

#Filter Data
predictors_freq  <- c("tclex_zipf", "clc_zipf", "tekcan_zipf")
predictors_psych <- c("imagery", "concreteness", "syllable_count", "char_count")
outcome          <- "overall_aoa_mean"

model_data <- df %>%
  select(all_of(c(outcome, predictors_freq, predictors_psych))) %>%
  drop_na() %>%
  rename(
    TCLex          = tclex_zipf,
    CLC            = clc_zipf,
    Göz_2003       = tekcan_zipf,
    Imageability   = imagery,
    Concreteness   = concreteness,
    Syllable_Count = syllable_count,
    Char_Count     = char_count
  )

cat(paste("--- Words retained after removing all zero-frequency rows:", nrow(model_data), "of 600 ---\n"))

# Update predictor name vectors
predictors_freq  <- c("TCLex", "CLC", "Göz_2003")
predictors_psych <- c("Imageability", "Concreteness", "Syllable_Count", "Char_Count")

#Scale Psycholinguisitic Predictors
model_data <- model_data %>%
  mutate(across(all_of(predictors_psych), scale))

#Set up Elastic Net with Repeated Cross-Validation
train_control <- trainControl(
  method      = "repeatedcv",
  number      = 10,
  repeats     = 10,
  verboseIter = FALSE
)

tune_grid <- expand.grid(
  alpha  = seq(0.1, 0.9, by = 0.1),
  lambda = seq(0.001, 0.1, length.out = 50)
)

stopifnot(all(tune_grid$alpha > 0 & tune_grid$alpha < 1))

#Train Elastic Net
set.seed(123)
en_model <- train(
  overall_aoa_mean ~ .,
  data      = model_data,
  method    = "glmnet",
  trControl = train_control,
  tuneGrid  = tune_grid
)

#Model Performance
cat("\n Best Model Hyperparameters\n")
print(en_model$bestTune)
best_r2 <- max(en_model$results$Rsquared)
cat(paste("Total Variance Explained (R2):", round(best_r2, 4), "\n"))

#Variable Importance
importance <- varImp(en_model, scale = TRUE)
cat("\n Relative Variable Importance \n")
print(importance)

#Coefficients
best_coefs <- coef(en_model$finalModel, en_model$bestTune$lambda)
cat("\n Regression Coefficients \n")
print(best_coefs)

#Importance Plot
plot(importance, main = "Variable Importance for AoA Prediction")

#Summary
cat("\n REPORTING SUMMARY \n")
cat("Words in model:", nrow(model_data))
cat("R2:",     round(max(en_model$results$Rsquared), 4), "\n")
cat("Alpha:",  en_model$bestTune$alpha,  "\n")
cat("Lambda:", en_model$bestTune$lambda, "\n")

cat("\n Coefficients \n")
print(coef(en_model$finalModel, en_model$bestTune$lambda))

cat("\n Variable Importance \n")
print(varImp(en_model, scale = TRUE)$importance)



# Top alpha/lambda combinations by R²
cat("\n Top Tuning Combinations by R²\n")
en_model$results %>%
  select(alpha, lambda, Rsquared) %>%
  arrange(desc(Rsquared)) %>%
  head(20) %>%
  print()