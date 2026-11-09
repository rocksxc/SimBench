# Response to the applied-review concerns — v11

The revision tests the proposed remedies rather than selecting outcomes that would support a stronger score. The principal new evidence is a genuine planned-missing secondary analysis and a complete independent-forest experiment. It does not establish a typical exponential benefit or guarantee reviewer acceptance.

## 1. Is the fixed-form problem real?

We now analyze the actual PISA 2012 U.S. incomplete student archive. The original questionnaires used preassigned A/B/C forms to limit estimated response time to thirty minutes. Each contains a common section and two of three rotated blocks. The observed form is recorded in QUESTID. For a secondary analyst, the omitted answers cannot be recovered by switching to branching or asking for complete records after collection.

The task uses nine response indicators, three from each rotated block, and a common reported grade-repetition outcome. Every student has only six of these nine predictors. We train old and new block-averaged forest models on disjoint school sets using received blocks only, then evaluate on 2,441 students from 82 other schools. Reference marginals also come only from incomplete training records. There are no 500 complete target-population calibration records that could substitute for the audit.

Every block pair appears in a form. Expanding the Brier loss of an averaged block model therefore yields identifiable single-block and pair-block terms. This makes a proper scoring-rule comparison possible on the actual menu. Optimized scores estimate Brier improvement 0.001129, with a survey-asymptotic 95% interval [-0.002275, 0.004533]. Block/pair HT gives 0.001239 [-0.002094, 0.004572]; logistic multiple imputation gives 0.001239 [-0.002120, 0.004597]. None establishes improved Brier quality. Both models threshold to the negative class throughout the declared cube, so their deterministic accuracy contrast is identically zero; this is reported explicitly. Similar answers and widths do not establish superiority of the optimized score.

This is a performed secondary model comparison on real incomplete data. It is not a claim that OECD originally ran this model audit, that the selected target is a clinical diagnosis, or that a counterfactual branching benefit is observed. A new prospective collection could choose another design. Reported-answer invariance, allocation retained after common-target nonresponse, and survey inference assumptions are explicit. Nine form diagnostics do not certify invariance.

## 2. Did nonbinding budgets explain away the independent-model results?

Only partly. We checked each original task, rather than comparing separately aggregated feature counts and caps. Sixty of seventy probability-output independent-tree comparisons were already binding; their within-stratum population medians are 1.353 on SUSHI and 1.295 on SAPA, with global coefficients still near equality. Fifty-two of fifty-eight nonzero threshold comparisons are nonbinding. The structural explanation applies mainly to threshold outputs and cannot erase the probability-output negative evidence.

We add 240 prespecified independently fitted forest comparisons: WDBC, Spambase and Ionosphere; twenty splits each; 3/6/9/12 binarized features; cap three; twenty trees per model. The old/new models have disjoint training records. All 180 cases with six to twelve candidate features have more than three active features. The tested fitted fixed/menu-branch variance ratios have medians 1.085, 1.029 and 1.117 in those three datasets. No case exceeds 1.5, and the maximum over the full grid is 1.284. We retain the complete distribution.

The branch menu contains all fixed triples plus all component trees, and optimizes transcript scores jointly. It cannot compute the full forest in three queries. An oracle comparison on those same menus gives modest ratios too. The fixed-oracle lower bound divided by a feasible branch variance lower-bounds the unrestricted intrinsic gap; the menu ratio's upper endpoint does not preclude stronger adaptive protocols. Thus the conclusion is limited to the tested methods and populations. We do not claim that high active-feature/cap ratio guarantees a large advantage.

## 3. Calibration, baselines and costs

PISA uses no complete calibration records; the forest benchmark uses existing model-training records as a variance reference, with an independent evaluation split. Complete independent observations from the target population remain valid direct audit data. The previous 500-record calibration setting is now described as a controlled efficiency diagnostic. The main text retains transferred calibration and the restricted-pilot results, whose new records are charged.

PISA adds twenty logistic chained-equation imputations with Rubin pooling and the supplied eighty Fay replicate weights. This is a documented working-model implementation, not a claim to run the R mice package or to establish its coverage from incomplete data. A partial VAE is not added: no result in this revision depends on defeating every imputation model. Design-based scores retain validity under wrong reference marginals, conditional on the acquisition and measurement assumptions; imputation brings additional distributional assumptions.

A new cost plot uses every controlled task and shows the label-cost crossover for fixed forms versus complete records when the cap is relaxable. At zero label cost, median planned fixed/complete cost ratios are 0.726 and 0.731; at cost ten they are 1.427 and 1.299. Complete observations remain inadmissible under the immutable cap. Uncorrected imputation cannot be assigned a universal winning region from label cost alone because its bias and desired inference guarantee matter.

## 4. Presentation and remaining significance limits

The seven-page main narrative now begins its experiments with actual archival estimation, follows with independent forest updates, and treats the larger root/leaf CART gaps as controlled stress tests. Brier quality is the primary PISA target. The identifying block decomposition, menu limitation and survey intervals are defined explicitly. All 50 new implementation checks and 1,048 retained release checks pass.

The sharp minimax theorem remains a theoretical limit, rather than an empirical prediction for ordinary model updates. The new experiments improve the reality and honesty of the use case; they do not produce the previously missing large intrinsic gap for generic trained models. Whether this combination meets a particular ICML reviewer's significance threshold remains their judgment. No new independent reviewer simulation or positive-score claim is made. Human author proof verification is not attested by these automated checks.
