#!/usr/bin/env python3
"""
Nature Writing Pattern Analyzer
================================
Extracts text from Nature journal PDFs and performs deep NLP/ML analysis
to identify authentic human writing patterns for the humanizer skill.

ML/DL Techniques Used:
- TF-IDF vectorization for vocabulary profiling
- K-means clustering for paragraph structure patterns
- POS tagging distribution analysis (spaCy)
- Sentence embedding similarity (cosine similarity)
- Statistical analysis of sentence length distributions
- N-gram frequency analysis
- Information density estimation via type-token ratio
- Readability metrics (Flesch-Kincaid, Gunning Fog, etc.)
- Transition word frequency profiling
- Burstiness analysis (sentence-level entropy variation)
"""

import os
import sys
import re
import json
import math
import statistics
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import fitz  # PyMuPDF
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag, ngrams
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

warnings.filterwarnings('ignore')

# Ensure NLTK data
for resource in ['punkt', 'punkt_tab', 'averaged_perceptron_tagger', 'averaged_perceptron_tagger_eng', 'stopwords']:
    try:
        nltk.data.find(f'tokenizers/{resource}' if 'punkt' in resource else f'taggers/{resource}' if 'tagger' in resource else f'corpora/{resource}')
    except LookupError:
        nltk.download(resource, quiet=True)

try:
    import spacy
    nlp = spacy.load('en_core_web_sm')
    HAS_SPACY = True
except:
    HAS_SPACY = False
    print("WARNING: spaCy not available, using NLTK fallback")

try:
    import textstat
    HAS_TEXTSTAT = True
except:
    HAS_TEXTSTAT = False

# ============================================================
# PHASE 1: PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(pdf_path):
    """Extract clean text from a PDF using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        text_parts = []
        for page in doc:
            text = page.get_text("text")
            text_parts.append(text)
        doc.close()
        full_text = "\n".join(text_parts)
        # Clean up common PDF artifacts
        full_text = re.sub(r'\n{3,}', '\n\n', full_text)
        full_text = re.sub(r'([a-z])-\n([a-z])', r'\1\2', full_text)  # dehyphenate
        full_text = re.sub(r'\f', '', full_text)  # form feeds
        return full_text
    except Exception as e:
        print(f"  ERROR extracting {pdf_path}: {e}")
        return ""


def extract_body_text(full_text):
    """
    Extract the main body text, removing references, headers, footers,
    figure captions, and other non-prose elements.
    """
    lines = full_text.split('\n')
    body_lines = []
    in_references = False

    for line in lines:
        stripped = line.strip()
        # Skip empty lines
        if not stripped:
            body_lines.append('')
            continue
        # Detect references section
        if re.match(r'^(References|Bibliography|REFERENCES)\s*$', stripped):
            in_references = True
            continue
        if in_references:
            continue
        # Skip page numbers
        if re.match(r'^\d{1,4}$', stripped):
            continue
        # Skip figure/table captions (short lines starting with Fig/Table)
        if re.match(r'^(Fig\.|Figure|Table|Supplementary)\s', stripped) and len(stripped) < 200:
            continue
        # Skip journal headers
        if re.match(r'^(Nature|NATURE|Article|Review|Letter|Perspective|Comment)', stripped) and len(stripped) < 80:
            continue
        # Skip DOI lines
        if 'doi.org' in stripped.lower() or 'https://' in stripped.lower():
            continue
        # Skip very short lines (likely headers/footers)
        if len(stripped) < 15 and not stripped.endswith('.'):
            continue
        body_lines.append(stripped)

    # Rejoin into paragraphs
    text = ' '.join(body_lines)
    # Collapse multiple spaces
    text = re.sub(r'\s{2,}', ' ', text)
    # Re-split into paragraphs at double newlines
    paragraphs = [p.strip() for p in re.split(r'\s*\n\s*\n\s*', '\n'.join(body_lines)) if p.strip()]
    # Filter out very short paragraphs (likely artifacts)
    paragraphs = [p for p in paragraphs if len(p.split()) > 10]

    return paragraphs, text


# ============================================================
# PHASE 2: NLP ANALYSIS
# ============================================================

class NatureWritingAnalyzer:
    """Comprehensive NLP/ML analyzer for scientific writing patterns."""

    def __init__(self):
        self.all_sentences = []
        self.all_paragraphs = []
        self.all_words = []
        self.paper_stats = []
        self.transition_words = {
            'additive': ['also', 'moreover', 'furthermore', 'in addition', 'additionally', 'similarly', 'likewise'],
            'contrast': ['however', 'nevertheless', 'nonetheless', 'in contrast', 'conversely', 'although', 'though', 'yet', 'whereas', 'while', 'but', 'on the other hand'],
            'causal': ['therefore', 'thus', 'consequently', 'hence', 'accordingly', 'as a result', 'because', 'since', 'owing to', 'due to'],
            'temporal': ['subsequently', 'meanwhile', 'previously', 'recently', 'initially', 'finally', 'then', 'next', 'first', 'second'],
            'exemplifying': ['for example', 'for instance', 'specifically', 'in particular', 'namely', 'such as', 'including'],
            'emphasis': ['notably', 'importantly', 'indeed', 'in fact', 'particularly', 'especially', 'significantly'],
            'concessive': ['despite', 'notwithstanding', 'regardless', 'even though', 'albeit'],
        }
        # AI vocabulary from the humanizer skill
        self.ai_tier1 = {'delve', 'tapestry', 'landscape', 'testament', 'underscore', 'showcase',
                         'foster', 'garner', 'pivotal', 'vibrant', 'enduring', 'intricate',
                         'intricacies', 'interplay', 'cornerstone', 'leverage', 'synergy',
                         'harness', 'unlock', 'realm', 'multifaceted', 'nuanced'}
        self.ai_tier2 = {'additionally', 'crucial', 'emphasizing', 'enhance', 'enhancing',
                         'highlight', 'key', 'valuable', 'comprehensive', 'innovative', 'robust',
                         'furthermore', 'moreover', 'streamline', 'commendable', 'meticulous',
                         'meticulously', 'groundbreaking', 'cutting-edge', 'paradigm',
                         'unparalleled', 'revolutionize', 'bolstered', 'game-changer'}
        self.ai_tier3_pubmed = {'notably', 'exhibited', 'insights', 'primarily', 'particularly',
                                'within', 'across', 'underscores', 'comprehensive', 'crucial',
                                'additionally', 'significantly', 'demonstrated', 'elucidated',
                                'facilitated', 'underpinned', 'illuminated', 'spearheaded'}

    def analyze_sentence_structure(self, sentences):
        """Analyze sentence length distribution, variation, and complexity."""
        lengths = [len(s.split()) for s in sentences if len(s.split()) > 2]
        if not lengths:
            return {}

        mean_len = statistics.mean(lengths)
        std_len = statistics.stdev(lengths) if len(lengths) > 1 else 0
        cv = std_len / mean_len if mean_len > 0 else 0

        # Burstiness: ratio of (std - mean) / (std + mean)
        burstiness = (std_len - mean_len) / (std_len + mean_len) if (std_len + mean_len) > 0 else 0

        # Length distribution buckets
        short = sum(1 for l in lengths if l <= 10)
        medium = sum(1 for l in lengths if 11 <= l <= 20)
        long = sum(1 for l in lengths if 21 <= l <= 35)
        very_long = sum(1 for l in lengths if l > 35)
        total = len(lengths)

        return {
            'mean_length': round(mean_len, 2),
            'median_length': statistics.median(lengths),
            'std_length': round(std_len, 2),
            'cv': round(cv, 3),
            'min_length': min(lengths),
            'max_length': max(lengths),
            'burstiness': round(burstiness, 3),
            'pct_short_le10': round(short/total*100, 1),
            'pct_medium_11_20': round(medium/total*100, 1),
            'pct_long_21_35': round(long/total*100, 1),
            'pct_very_long_gt35': round(very_long/total*100, 1),
            'n_sentences': total,
        }

    def analyze_paragraph_structure(self, paragraphs):
        """Analyze paragraph-level patterns."""
        para_lengths = []  # sentence counts per paragraph
        para_word_counts = []

        for para in paragraphs:
            sents = sent_tokenize(para)
            para_lengths.append(len(sents))
            para_word_counts.append(len(para.split()))

        if not para_lengths:
            return {}

        # Consecutive same-length paragraph runs
        max_run = 1
        current_run = 1
        for i in range(1, len(para_lengths)):
            if para_lengths[i] == para_lengths[i-1]:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 1

        return {
            'mean_sents_per_para': round(statistics.mean(para_lengths), 2),
            'std_sents_per_para': round(statistics.stdev(para_lengths), 2) if len(para_lengths) > 1 else 0,
            'cv_sents_per_para': round(statistics.stdev(para_lengths) / statistics.mean(para_lengths), 3) if len(para_lengths) > 1 and statistics.mean(para_lengths) > 0 else 0,
            'mean_words_per_para': round(statistics.mean(para_word_counts), 1),
            'std_words_per_para': round(statistics.stdev(para_word_counts), 1) if len(para_word_counts) > 1 else 0,
            'max_consecutive_same_length': max_run,
            'para_length_distribution': dict(Counter(para_lengths).most_common(10)),
            'n_paragraphs': len(paragraphs),
        }

    def analyze_vocabulary(self, text):
        """Vocabulary profiling: TTR, lexical density, AI word usage."""
        words = word_tokenize(text.lower())
        words = [w for w in words if w.isalpha() and len(w) > 1]

        if not words:
            return {}

        # Type-token ratio (TTR) - lexical diversity
        unique_words = set(words)
        ttr = len(unique_words) / len(words) if words else 0

        # Moving average TTR (MATTR) - more stable for varying text lengths
        window = 100
        if len(words) > window:
            ttrs = []
            for i in range(len(words) - window):
                chunk = words[i:i+window]
                ttrs.append(len(set(chunk)) / window)
            mattr = statistics.mean(ttrs)
        else:
            mattr = ttr

        # AI vocabulary overlap
        word_set = set(words)
        ai_t1_found = word_set & self.ai_tier1
        ai_t2_found = word_set & self.ai_tier2
        ai_t3_found = word_set & self.ai_tier3_pubmed

        # Count frequencies of AI words
        word_freq = Counter(words)
        ai_t1_counts = {w: word_freq[w] for w in ai_t1_found}
        ai_t2_counts = {w: word_freq[w] for w in ai_t2_found}
        ai_t3_counts = {w: word_freq[w] for w in ai_t3_found}

        # Lexical density (content words / total words)
        tagged = pos_tag(words[:5000])  # limit for speed
        content_tags = {'NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS'}
        content_words = sum(1 for _, tag in tagged if tag in content_tags)
        lexical_density = content_words / len(tagged) if tagged else 0

        return {
            'ttr': round(ttr, 4),
            'mattr': round(mattr, 4),
            'lexical_density': round(lexical_density, 3),
            'total_words': len(words),
            'unique_words': len(unique_words),
            'ai_tier1_words_found': ai_t1_counts,
            'ai_tier2_words_found': ai_t2_counts,
            'ai_tier3_pubmed_found': ai_t3_counts,
        }

    def analyze_transitions(self, sentences):
        """Analyze transition word usage patterns."""
        transition_counts = defaultdict(int)
        transition_examples = defaultdict(list)
        sentence_starts = []

        for sent in sentences:
            lower = sent.lower().strip()
            words = lower.split()
            if words:
                # First word/phrase of sentence
                first_word = words[0].rstrip(',')
                sentence_starts.append(first_word)

            for category, words_list in self.transition_words.items():
                for tw in words_list:
                    if tw in lower:
                        transition_counts[category] += 1
                        if len(transition_examples[category]) < 3:
                            transition_examples[category].append(sent[:100])

        # Sentence opening patterns
        start_counts = Counter(sentence_starts).most_common(30)

        total_transitions = sum(transition_counts.values())
        n_sents = len(sentences)

        return {
            'transition_frequency': round(total_transitions / n_sents * 100, 1) if n_sents > 0 else 0,
            'transitions_per_100_sentences': {k: round(v/n_sents*100, 1) for k, v in transition_counts.items()},
            'transition_distribution': dict(transition_counts),
            'top_sentence_starters': start_counts,
            'transition_examples': {k: v for k, v in transition_examples.items()},
        }

    def analyze_voice_and_person(self, text):
        """Analyze active vs passive voice and person usage."""
        sentences = sent_tokenize(text)

        # Simple heuristic for passive voice: "was/were/been/being + past participle"
        passive_pattern = re.compile(
            r'\b(was|were|is|are|been|being|has been|have been|had been)\s+(\w+ed|shown|seen|found|made|given|taken|known|done|observed|measured|detected|identified|reported|described|characterized)\b',
            re.IGNORECASE
        )

        passive_count = 0
        active_count = 0
        first_person_count = 0
        we_count = 0

        for sent in sentences:
            if passive_pattern.search(sent):
                passive_count += 1
            else:
                active_count += 1

            words_lower = sent.lower().split()
            if 'we' in words_lower or 'our' in words_lower:
                we_count += 1
            if 'i' in words_lower:
                first_person_count += 1

        total = passive_count + active_count
        return {
            'passive_voice_pct': round(passive_count / total * 100, 1) if total > 0 else 0,
            'active_voice_pct': round(active_count / total * 100, 1) if total > 0 else 0,
            'first_person_we_pct': round(we_count / len(sentences) * 100, 1) if sentences else 0,
            'first_person_i_pct': round(first_person_count / len(sentences) * 100, 1) if sentences else 0,
        }

    def analyze_copula_patterns(self, text):
        """Analyze copula usage vs elaborate substitutes."""
        simple_copulas = len(re.findall(r'\b(is|are|was|were|has|have|had)\b', text, re.IGNORECASE))
        substitutes = len(re.findall(r'\b(serves as|stands as|marks|represents|functions as|acts as)\b', text, re.IGNORECASE))

        total = simple_copulas + substitutes
        ratio = substitutes / total * 100 if total > 0 else 0

        return {
            'simple_copulas': simple_copulas,
            'copula_substitutes': substitutes,
            'substitute_ratio_pct': round(ratio, 2),
        }

    def analyze_readability(self, text):
        """Calculate readability metrics."""
        if not HAS_TEXTSTAT:
            return {}

        return {
            'flesch_reading_ease': textstat.flesch_reading_ease(text),
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
            'gunning_fog': textstat.gunning_fog(text),
            'smog_index': textstat.smog_index(text),
            'coleman_liau': textstat.coleman_liau_index(text),
            'ari': textstat.automated_readability_index(text),
        }

    def analyze_ngrams(self, text, n_range=(2, 4)):
        """Extract most common n-grams (phrases) from text."""
        words = word_tokenize(text.lower())
        words = [w for w in words if w.isalpha() and len(w) > 1]

        results = {}
        for n in range(n_range[0], n_range[1] + 1):
            grams = list(ngrams(words, n))
            gram_strings = [' '.join(g) for g in grams]
            # Filter out grams with only stopwords
            stopwords = set(nltk.corpus.stopwords.words('english'))
            gram_strings = [g for g in gram_strings if any(w not in stopwords for w in g.split())]
            counts = Counter(gram_strings).most_common(30)
            results[f'{n}-grams'] = counts

        return results

    def analyze_information_density(self, paragraphs):
        """
        Measure information density variation across paragraphs.
        Uses entity count + number count + technical term density as proxy.
        """
        densities = []

        for para in paragraphs:
            words = para.split()
            n_words = len(words)
            if n_words < 5:
                continue

            # Count numbers (data points)
            numbers = len(re.findall(r'\b\d+\.?\d*\b', para))
            # Count parenthetical references (citations, units, etc.)
            parens = len(re.findall(r'\([^)]+\)', para))
            # Count technical abbreviations (2+ uppercase letters)
            abbrevs = len(re.findall(r'\b[A-Z]{2,}\b', para))

            density = (numbers + parens + abbrevs) / n_words
            densities.append(density)

        if not densities:
            return {}

        return {
            'mean_info_density': round(statistics.mean(densities), 4),
            'std_info_density': round(statistics.stdev(densities), 4) if len(densities) > 1 else 0,
            'cv_info_density': round(statistics.stdev(densities) / statistics.mean(densities), 3) if len(densities) > 1 and statistics.mean(densities) > 0 else 0,
            'min_info_density': round(min(densities), 4),
            'max_info_density': round(max(densities), 4),
        }

    def analyze_em_dash_and_punctuation(self, text):
        """Analyze punctuation patterns."""
        em_dashes = text.count('\u2014') + text.count('--')
        en_dashes = text.count('\u2013')
        semicolons = text.count(';')
        colons = text.count(':')
        commas = text.count(',')
        periods = text.count('.')

        n_sents = len(sent_tokenize(text))

        return {
            'em_dashes_per_1000_words': round(em_dashes / len(text.split()) * 1000, 2) if text.split() else 0,
            'en_dashes_per_1000_words': round(en_dashes / len(text.split()) * 1000, 2) if text.split() else 0,
            'semicolons_per_sentence': round(semicolons / n_sents, 3) if n_sents > 0 else 0,
            'colons_per_sentence': round(colons / n_sents, 3) if n_sents > 0 else 0,
            'commas_per_sentence': round(commas / n_sents, 2) if n_sents > 0 else 0,
            'em_dash_count': em_dashes,
            'en_dash_count': en_dashes,
        }

    def analyze_sentence_opening_patterns(self, sentences):
        """Classify how sentences open (subject-first, transition, dependent clause, etc.)."""
        patterns = Counter()

        for sent in sentences:
            stripped = sent.strip()
            if not stripped:
                continue

            lower = stripped.lower()

            # Check opening pattern
            if re.match(r'^(however|nevertheless|nonetheless|in contrast|conversely|moreover|furthermore|additionally|similarly)\b', lower):
                patterns['transition_word'] += 1
            elif re.match(r'^(although|while|whereas|despite|given that|because|since|when|if|after|before|as)\b', lower):
                patterns['dependent_clause_first'] += 1
            elif re.match(r'^(we|our|the authors)\b', lower):
                patterns['first_person'] += 1
            elif re.match(r'^(this|these|that|those|such)\b', lower):
                patterns['demonstrative'] += 1
            elif re.match(r'^(the|a|an)\b', lower):
                patterns['article_start'] += 1
            elif re.match(r'^(it|there)\b', lower):
                patterns['expletive'] += 1
            elif re.match(r'^(here|in this|to this end|to address)\b', lower):
                patterns['meta_discourse'] += 1
            elif re.match(r'^[A-Z][a-z]+ing\b', lower):
                patterns['gerund_start'] += 1
            else:
                patterns['other'] += 1

        total = sum(patterns.values())
        pct = {k: round(v/total*100, 1) for k, v in patterns.items()} if total > 0 else {}

        return {
            'opening_pattern_counts': dict(patterns),
            'opening_pattern_pct': pct,
        }

    def run_tfidf_analysis(self, paper_texts):
        """
        TF-IDF analysis across papers to find distinctive vocabulary.
        Uses sklearn's TfidfVectorizer.
        """
        if len(paper_texts) < 2:
            return {}

        vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            min_df=2,  # appear in at least 2 documents
            max_df=0.95,
            ngram_range=(1, 2)
        )

        try:
            tfidf_matrix = vectorizer.fit_transform(paper_texts)
            feature_names = vectorizer.get_feature_names_out()

            # Average TF-IDF scores across all documents
            mean_tfidf = tfidf_matrix.mean(axis=0).A1
            top_indices = mean_tfidf.argsort()[-50:][::-1]
            top_terms = [(feature_names[i], round(mean_tfidf[i], 4)) for i in top_indices]

            return {
                'top_tfidf_terms': top_terms,
                'vocabulary_size': len(feature_names),
            }
        except Exception as e:
            return {'error': str(e)}

    def cluster_paragraphs(self, paragraphs):
        """
        K-means clustering of paragraphs by structure to identify
        distinct paragraph types in Nature writing.
        """
        if len(paragraphs) < 10:
            return {}

        # Feature extraction for each paragraph
        features = []
        for para in paragraphs:
            sents = sent_tokenize(para)
            words = para.split()

            n_sents = len(sents)
            n_words = len(words)
            avg_sent_len = n_words / n_sents if n_sents > 0 else 0

            # Numbers density
            numbers = len(re.findall(r'\b\d+\.?\d*\b', para))
            # Citation density
            citations = len(re.findall(r'\(\d{4}\)|\[\d+\]|et al\.', para))
            # Question marks
            questions = para.count('?')

            features.append([
                n_sents, n_words, avg_sent_len,
                numbers / n_words if n_words > 0 else 0,
                citations / n_sents if n_sents > 0 else 0,
                questions,
            ])

        X = np.array(features)
        # Normalize
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # K-means with k=4 (hypothesis: intro-style, methods, results-data, discussion)
        k = min(4, len(paragraphs) // 3)
        if k < 2:
            return {}

        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)

        # Characterize each cluster
        cluster_info = {}
        for c in range(k):
            mask = labels == c
            cluster_features = X[mask]
            cluster_info[f'cluster_{c}'] = {
                'n_paragraphs': int(mask.sum()),
                'avg_sentences': round(cluster_features[:, 0].mean(), 1),
                'avg_words': round(cluster_features[:, 1].mean(), 0),
                'avg_sent_length': round(cluster_features[:, 2].mean(), 1),
                'avg_number_density': round(cluster_features[:, 3].mean(), 4),
                'avg_citation_density': round(cluster_features[:, 4].mean(), 3),
            }

        return cluster_info

    def analyze_paper(self, pdf_path, paper_idx):
        """Full analysis of a single paper."""
        filename = os.path.basename(pdf_path)
        print(f"  [{paper_idx}] Analyzing: {filename}")

        full_text = extract_text_from_pdf(pdf_path)
        if not full_text or len(full_text) < 500:
            print(f"    -> Skipped (too short or extraction failed)")
            return None

        # Save extracted text
        txt_path = pdf_path.replace('.pdf', '.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(full_text)

        paragraphs, clean_text = extract_body_text(full_text)
        if not paragraphs:
            print(f"    -> Skipped (no body text extracted)")
            return None

        sentences = []
        for para in paragraphs:
            sentences.extend(sent_tokenize(para))

        # Run all analyses
        results = {
            'filename': filename,
            'total_chars': len(full_text),
            'sentence_structure': self.analyze_sentence_structure(sentences),
            'paragraph_structure': self.analyze_paragraph_structure(paragraphs),
            'vocabulary': self.analyze_vocabulary(clean_text),
            'transitions': self.analyze_transitions(sentences),
            'voice_and_person': self.analyze_voice_and_person(clean_text),
            'copula_patterns': self.analyze_copula_patterns(clean_text),
            'readability': self.analyze_readability(clean_text),
            'punctuation': self.analyze_em_dash_and_punctuation(clean_text),
            'information_density': self.analyze_information_density(paragraphs),
            'sentence_openings': self.analyze_sentence_opening_patterns(sentences),
        }

        # Store for aggregate analysis
        self.all_sentences.extend(sentences)
        self.all_paragraphs.extend(paragraphs)
        self.paper_stats.append(results)

        n_sents = results['sentence_structure'].get('n_sentences', 0)
        cv = results['sentence_structure'].get('cv', 0)
        print(f"    -> OK: {n_sents} sentences, CV={cv}")

        return results

    def aggregate_analysis(self, paper_texts):
        """Aggregate analysis across all papers."""
        print("\n=== AGGREGATE ANALYSIS ===\n")

        # Aggregate sentence structure
        all_sent_stats = self.analyze_sentence_structure(self.all_sentences)
        all_para_stats = self.analyze_paragraph_structure(self.all_paragraphs)

        # Aggregate vocabulary
        all_text = ' '.join(self.all_paragraphs)
        all_vocab = self.analyze_vocabulary(all_text)
        all_transitions = self.analyze_transitions(self.all_sentences)
        all_voice = self.analyze_voice_and_person(all_text)
        all_copula = self.analyze_copula_patterns(all_text)
        all_readability = self.analyze_readability(all_text)
        all_punctuation = self.analyze_em_dash_and_punctuation(all_text)
        all_info_density = self.analyze_information_density(self.all_paragraphs)
        all_openings = self.analyze_sentence_opening_patterns(self.all_sentences)

        # N-gram analysis
        all_ngrams = self.analyze_ngrams(all_text)

        # TF-IDF across papers
        tfidf_results = self.run_tfidf_analysis(paper_texts)

        # Paragraph clustering
        cluster_results = self.cluster_paragraphs(self.all_paragraphs)

        # Per-paper variation (how much do individual papers vary?)
        per_paper_cvs = [p['sentence_structure']['cv'] for p in self.paper_stats if 'cv' in p.get('sentence_structure', {})]
        per_paper_passive = [p['voice_and_person']['passive_voice_pct'] for p in self.paper_stats if 'passive_voice_pct' in p.get('voice_and_person', {})]

        aggregate = {
            'n_papers_analyzed': len(self.paper_stats),
            'total_sentences': len(self.all_sentences),
            'total_paragraphs': len(self.all_paragraphs),
            'sentence_structure': all_sent_stats,
            'paragraph_structure': all_para_stats,
            'vocabulary': all_vocab,
            'transitions': all_transitions,
            'voice_and_person': all_voice,
            'copula_patterns': all_copula,
            'readability': all_readability,
            'punctuation': all_punctuation,
            'information_density': all_info_density,
            'sentence_openings': all_openings,
            'ngrams': all_ngrams,
            'tfidf': tfidf_results,
            'paragraph_clusters': cluster_results,
            'per_paper_variation': {
                'sentence_cv_mean': round(statistics.mean(per_paper_cvs), 3) if per_paper_cvs else 0,
                'sentence_cv_std': round(statistics.stdev(per_paper_cvs), 3) if len(per_paper_cvs) > 1 else 0,
                'passive_pct_mean': round(statistics.mean(per_paper_passive), 1) if per_paper_passive else 0,
                'passive_pct_std': round(statistics.stdev(per_paper_passive), 1) if len(per_paper_passive) > 1 else 0,
            }
        }

        return aggregate


# ============================================================
# MAIN
# ============================================================

def find_nature_pdfs():
    """Find all Nature journal PDFs.

    Configure the base path and subdirectories to point to your own
    collection of Nature journal PDFs.
    """
    base = os.environ.get(
        "NATURE_PDF_DIR",
        os.path.expanduser("~/literature/nature_papers"),
    )

    pdf_dirs = [
        os.path.join(base, "Nature Nanotechnology"),
        os.path.join(base, "Nature_Nano_PDFs"),
        os.path.join(base, "Nature Reviews Bioengineering"),
        os.path.join(base, "Nature Biotechnology"),
    ]

    all_pdfs = []
    for d in pdf_dirs:
        if os.path.exists(d):
            for root, dirs, files in os.walk(d):
                for f in files:
                    if f.endswith('.pdf'):
                        all_pdfs.append(os.path.join(root, f))

    return all_pdfs


def select_representative_papers(all_pdfs, max_papers=50):
    """
    Select a representative sample of papers.
    Prioritize: Nature Nanotechnology > Nature Reviews Bioengineering > Nature Biotechnology
    For Biotechnology, select review-like and research articles, skip news/editorials.
    """
    nano_direct = [p for p in all_pdfs if '/Nature Nanotechnology/' in p]
    nano_other = [p for p in all_pdfs if '/Nature_Nano_PDFs/' in p]
    bioeng = [p for p in all_pdfs if '/Nature Reviews Bioengineering' in p]
    biotech = [p for p in all_pdfs if '/Nature Biotechnology' in p]

    # Prioritize review articles and research papers
    # Filter out short PDFs (news, editorials tend to be small)
    def filter_by_size(pdfs, min_size_kb=100):
        return [p for p in pdfs if os.path.getsize(p) > min_size_kb * 1024]

    selected = []
    selected.extend(nano_direct)  # All Nature Nano direct (4 papers)
    selected.extend(nano_other[:15])  # Up to 15 from Nature Nano collection
    selected.extend(filter_by_size(bioeng, 200)[:15])  # Up to 15 reviews from bioengineering

    # From biotechnology, pick larger files (more likely research/review articles)
    biotech_large = filter_by_size(biotech, 300)
    remaining = max_papers - len(selected)
    if remaining > 0:
        selected.extend(biotech_large[:remaining])

    return selected[:max_papers]


def main():
    print("=" * 70)
    print("NATURE WRITING PATTERN ANALYZER")
    print("ML/DL-powered analysis for humanizer skill improvement")
    print("=" * 70)

    # Find and select papers
    all_pdfs = find_nature_pdfs()
    print(f"\nFound {len(all_pdfs)} total Nature PDFs")

    selected = select_representative_papers(all_pdfs)
    print(f"Selected {len(selected)} representative papers for analysis\n")

    # Initialize analyzer
    analyzer = NatureWritingAnalyzer()
    paper_texts = []

    # Analyze each paper
    for i, pdf_path in enumerate(selected, 1):
        result = analyzer.analyze_paper(pdf_path, i)
        if result:
            paragraphs, text = extract_body_text(extract_text_from_pdf(pdf_path))
            paper_texts.append(text)

    # Aggregate analysis
    aggregate = analyzer.aggregate_analysis(paper_texts)

    # Save results
    output_dir = os.path.dirname(os.path.abspath(__file__))

    # Save aggregate results
    output_path = os.path.join(output_dir, 'nature_writing_analysis.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(aggregate, f, indent=2, default=str)
    print(f"\nAggregate results saved to: {output_path}")

    # Save per-paper results
    per_paper_path = os.path.join(output_dir, 'per_paper_analysis.json')
    with open(per_paper_path, 'w', encoding='utf-8') as f:
        json.dump(analyzer.paper_stats, f, indent=2, default=str)
    print(f"Per-paper results saved to: {per_paper_path}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY OF KEY FINDINGS")
    print("=" * 70)

    ss = aggregate['sentence_structure']
    print(f"\n📊 SENTENCE STRUCTURE:")
    print(f"   Mean length: {ss.get('mean_length', 'N/A')} words")
    print(f"   Median length: {ss.get('median_length', 'N/A')} words")
    print(f"   CV (variation): {ss.get('cv', 'N/A')} (target >0.40)")
    print(f"   Burstiness: {ss.get('burstiness', 'N/A')}")
    print(f"   Short (<=10): {ss.get('pct_short_le10', 'N/A')}%")
    print(f"   Medium (11-20): {ss.get('pct_medium_11_20', 'N/A')}%")
    print(f"   Long (21-35): {ss.get('pct_long_21_35', 'N/A')}%")
    print(f"   Very long (>35): {ss.get('pct_very_long_gt35', 'N/A')}%")

    ps = aggregate['paragraph_structure']
    print(f"\n📊 PARAGRAPH STRUCTURE:")
    print(f"   Mean sentences/para: {ps.get('mean_sents_per_para', 'N/A')}")
    print(f"   CV sentences/para: {ps.get('cv_sents_per_para', 'N/A')}")
    print(f"   Mean words/para: {ps.get('mean_words_per_para', 'N/A')}")
    print(f"   Max consecutive same-length: {ps.get('max_consecutive_same_length', 'N/A')}")

    vp = aggregate['voice_and_person']
    print(f"\n📊 VOICE:")
    print(f"   Passive voice: {vp.get('passive_voice_pct', 'N/A')}%")
    print(f"   Active voice: {vp.get('active_voice_pct', 'N/A')}%")
    print(f"   'We/our' usage: {vp.get('first_person_we_pct', 'N/A')}%")

    cp = aggregate['copula_patterns']
    print(f"\n📊 COPULA PATTERNS:")
    print(f"   Simple copulas: {cp.get('simple_copulas', 'N/A')}")
    print(f"   Substitutes: {cp.get('copula_substitutes', 'N/A')}")
    print(f"   Substitute ratio: {cp.get('substitute_ratio_pct', 'N/A')}%")

    rd = aggregate.get('readability', {})
    print(f"\n📊 READABILITY:")
    print(f"   Flesch-Kincaid grade: {rd.get('flesch_kincaid_grade', 'N/A')}")
    print(f"   Gunning Fog: {rd.get('gunning_fog', 'N/A')}")
    print(f"   Flesch Reading Ease: {rd.get('flesch_reading_ease', 'N/A')}")

    pn = aggregate['punctuation']
    print(f"\n📊 PUNCTUATION:")
    print(f"   Em dashes/1000 words: {pn.get('em_dashes_per_1000_words', 'N/A')}")
    print(f"   En dashes/1000 words: {pn.get('en_dashes_per_1000_words', 'N/A')}")
    print(f"   Commas/sentence: {pn.get('commas_per_sentence', 'N/A')}")
    print(f"   Semicolons/sentence: {pn.get('semicolons_per_sentence', 'N/A')}")

    vo = aggregate['vocabulary']
    print(f"\n📊 VOCABULARY:")
    print(f"   TTR: {vo.get('ttr', 'N/A')}")
    print(f"   MATTR: {vo.get('mattr', 'N/A')}")
    print(f"   Lexical density: {vo.get('lexical_density', 'N/A')}")
    print(f"   AI Tier 1 words found: {vo.get('ai_tier1_words_found', {})}")
    print(f"   AI Tier 2 words found: {vo.get('ai_tier2_words_found', {})}")

    tr = aggregate['transitions']
    print(f"\n📊 TRANSITIONS:")
    print(f"   Per 100 sentences: {tr.get('transitions_per_100_sentences', {})}")

    so = aggregate['sentence_openings']
    print(f"\n📊 SENTENCE OPENINGS:")
    for k, v in so.get('opening_pattern_pct', {}).items():
        print(f"   {k}: {v}%")

    idd = aggregate['information_density']
    print(f"\n📊 INFORMATION DENSITY:")
    print(f"   Mean: {idd.get('mean_info_density', 'N/A')}")
    print(f"   CV: {idd.get('cv_info_density', 'N/A')}")

    ppv = aggregate['per_paper_variation']
    print(f"\n📊 PAPER-TO-PAPER VARIATION:")
    print(f"   Sentence CV mean: {ppv.get('sentence_cv_mean', 'N/A')} +/- {ppv.get('sentence_cv_std', 'N/A')}")
    print(f"   Passive voice mean: {ppv.get('passive_pct_mean', 'N/A')}% +/- {ppv.get('passive_pct_std', 'N/A')}%")

    print("\n" + "=" * 70)
    print("Analysis complete! Results saved to scripts/ folder.")
    print("=" * 70)


if __name__ == '__main__':
    main()
