library(tidyverse)
library(knitr)
library(kableExtra)

file_path <- '../TCLex-AoA.tsv'

df <- readr::read_tsv(file_path)
df <- df %>%
  mutate(
    clc_normalized = readr::parse_number(clc_normalized)
  )

# Zeros kept — smoothing + log transform (Zipf)

df_keep_zeros <- df %>%
  mutate(
    tclex_zipf  = log10(tclex_normalized + 0.001) + 3,
    clc_zipf    = log10(clc_normalized      + 0.001) + 3,
    tekcan_zipf = log10(tekcan_frequency    + 0.001) + 3
  )

test1 <- cor.test(df_keep_zeros$tclex_zipf,  df_keep_zeros$clc_zipf)
test2 <- cor.test(df_keep_zeros$tclex_zipf,  df_keep_zeros$tekcan_zipf)
test3 <- cor.test(df_keep_zeros$clc_zipf,    df_keep_zeros$tekcan_zipf)

n1 <- sum(complete.cases(df_keep_zeros$tclex_zipf,  df_keep_zeros$clc_zipf))
n2 <- sum(complete.cases(df_keep_zeros$tclex_zipf,  df_keep_zeros$tekcan_zipf))
n3 <- sum(complete.cases(df_keep_zeros$clc_zipf,    df_keep_zeros$tekcan_zipf))

results_keep_zeros <- data.frame(
  Database_Pair = c(
    "TCLex vs CLC",
    "TCLex vs \\citet{goz2003yazili}",
    "CLC vs \\citet{goz2003yazili}"
  ),
  r = round(c(test1$estimate, test2$estimate, test3$estimate), 2),
  p = ifelse(
    c(test1$p.value, test2$p.value, test3$p.value) < .001,
    "$<$.001",
    as.character(round(c(test1$p.value, test2$p.value, test3$p.value), 3))
  ),
  N = c(n1, n2, n3)
)


# Zeros removed pairwise — log transform (Zipf)

df_no_zeros <- df %>%
  mutate(
    tclex_zipf  = ifelse(tclex_normalized <= 0, NA, log10(tclex_normalized) + 3),
    clc_zipf    = ifelse(clc_normalized      <= 0, NA, log10(clc_normalized)      + 3),
    tekcan_zipf = ifelse(tekcan_frequency    <= 0, NA, log10(tekcan_frequency)    + 3)
  )

test1_no0 <- cor.test(df_no_zeros$tclex_zipf,  df_no_zeros$clc_zipf,
                      use = "pairwise.complete.obs")
test2_no0 <- cor.test(df_no_zeros$tclex_zipf,  df_no_zeros$tekcan_zipf,
                      use = "pairwise.complete.obs")
test3_no0 <- cor.test(df_no_zeros$clc_zipf,    df_no_zeros$tekcan_zipf,
                      use = "pairwise.complete.obs")

n1_no0 <- sum(complete.cases(df_no_zeros$tclex_zipf,  df_no_zeros$clc_zipf))
n2_no0 <- sum(complete.cases(df_no_zeros$tclex_zipf,  df_no_zeros$tekcan_zipf))
n3_no0 <- sum(complete.cases(df_no_zeros$clc_zipf,    df_no_zeros$tekcan_zipf))

results_no_zeros <- data.frame(
  Database_Pair = c(
    "TCLex vs CLC",
    "TCLex vs \\citet{goz2003yazili}",
    "CLC vs \\citet{goz2003yazili}"
  ),
  r = round(c(test1_no0$estimate, test2_no0$estimate, test3_no0$estimate), 2),
  p = ifelse(
    c(test1_no0$p.value, test2_no0$p.value, test3_no0$p.value) < .001,
    "$<$.001",
    as.character(round(c(test1_no0$p.value, test2_no0$p.value, test3_no0$p.value), 3))
  ),
  N = c(n1_no0, n2_no0, n3_no0)
)

#TABLE 1: Zeros kept

kable(
  results_keep_zeros,
  format   = "latex",
  booktabs = TRUE,
  escape   = FALSE,
  caption  = "Pearson correlations between word frequency Zipf scores across databases. Zero-frequency words were retained; a smoothing constant of 0.001 was added prior to log transformation.",
  label    = "tab:frequency_correlations_keep_zeros",
  col.names = c("Database Pair", "$r$", "$p$", "$N$")
) %>%
  kable_styling(
    latex_options = c("hold_position"),
    position      = "center"
  ) %>%
  footnote(
    general       = "Zipf = log\\textsubscript{10}(freq + 0.001) + 3.",
    general_title = "\\textit{Note.}",
    escape        = FALSE,
    footnote_as_chunk = TRUE
  )

#TABLE 2: Zeros removed

kable(
  results_no_zeros,
  format   = "latex",
  booktabs = TRUE,
  escape   = FALSE,
  caption  = "Pearson correlations between word frequency Zipf scores across databases. Zero-frequency words were excluded pairwise; $N$ varies across pairs accordingly.",
  label    = "tab:frequency_correlations_no_zeros",
  col.names = c("Database Pair", "$r$", "$p$", "$N$")
) %>%
  kable_styling(
    latex_options = c("hold_position"),
    position      = "center"
  ) %>%
  footnote(
    general       = "Zipf = log\\textsubscript{10}(freq) + 3. Zeros set to \\textit{NA} before correlation; exclusion is pairwise.",
    general_title = "Note",
    escape        = FALSE,
    footnote_as_chunk = TRUE
  )