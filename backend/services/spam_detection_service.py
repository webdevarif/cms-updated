"""
Spam detection service for comments and reviews.
Provides comprehensive spam detection with link checking, profanity filtering, and repeat content detection.
"""
import logging
import re

from apps.notifications.services import NotificationService
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class SpamDetectionService:
    """
    Service for detecting spam in comments and reviews.
    Uses multiple detection methods: links, profanity, repeat content, user patterns.
    """

    # Profanity list (basic - can be expanded)
    PROFANITY_LIST = {
        "badword1",
        "badword2",
        "spamword",
        "inappropriate",
        "offensive",
        # Add more profanity words as needed
    }

    # Spam patterns
    SPAM_PATTERNS = [
        r"http[s]?://[^\s]+",  # URLs
        r"www\.[^\s]+",  # Web addresses
        r"\b\d{10,}\b",  # Long phone numbers
        r"\b[A-Z]{5,}\b",  # ALL CAPS words longer than 5 chars
        r"\b\w+@\w+\.\w+\b",  # Email addresses
    ]

    # Auto-reject thresholds
    AUTO_REJECT_LINKS = 2  # More than 2 links = auto-reject
    AUTO_REJECT_PROFANITY = 3  # More than 3 profanity words = auto-reject
    SIMILARITY_THRESHOLD = 0.8  # 80% similar to existing content

    @staticmethod
    def check_content(content, user, content_type="comment", store=None):
        """
        Comprehensive spam check for content.

        Args:
            content: Text content to check
            user: User who submitted the content
            content_type: 'comment' or 'review'
            store: Store instance

        Returns:
            dict: {
                'is_spam': bool,
                'auto_reject': bool,
                'reasons': list of str,
                'score': float (0-1, higher = more spammy),
                'recommendation': str ('approve', 'reject', 'flag')
            }
        """
        if not content or not content.strip():
            return {
                "is_spam": False,
                "auto_reject": False,
                "reasons": [],
                "score": 0.0,
                "recommendation": "approve",
            }

        reasons = []
        score = 0.0

        # Check for links/URLs
        link_score, link_reasons = SpamDetectionService._check_links(content)
        score += link_score
        reasons.extend(link_reasons)

        # Check for profanity
        profanity_score, profanity_reasons = SpamDetectionService._check_profanity(content)
        score += profanity_score
        reasons.extend(profanity_reasons)

        # Check for repeat/similar content
        repeat_score, repeat_reasons = SpamDetectionService._check_repeat_content(
            content, user, content_type, store
        )
        score += repeat_score
        reasons.extend(repeat_reasons)

        # Check user patterns (rate limiting, etc.)
        user_score, user_reasons = SpamDetectionService._check_user_patterns(
            user, content_type, store
        )
        score += user_score
        reasons.extend(user_reasons)

        # Check content patterns (length, formatting, etc.)
        pattern_score, pattern_reasons = SpamDetectionService._check_content_patterns(content)
        score += pattern_score
        reasons.extend(pattern_reasons)

        # Determine if spam and auto-reject
        is_spam = score >= 0.5  # 50% threshold for spam
        auto_reject = SpamDetectionService._should_auto_reject(score, reasons)

        # Recommendation
        if auto_reject:
            recommendation = "reject"
        elif is_spam:
            recommendation = "flag"
        else:
            recommendation = "approve"

        return {
            "is_spam": is_spam,
            "auto_reject": auto_reject,
            "reasons": reasons,
            "score": min(score, 1.0),  # Cap at 1.0
            "recommendation": recommendation,
        }

    @staticmethod
    def _check_links(content):
        """Check for links and URLs in content."""
        score = 0.0
        reasons = []

        # Count URLs
        url_pattern = r"http[s]?://[^\s]+|www\.[^\s]+"
        urls = re.findall(url_pattern, content, re.IGNORECASE)
        url_count = len(urls)

        if url_count > 0:
            reasons.append(f"Contains {url_count} URL(s)")
            score += min(url_count * 0.3, 0.8)  # Each URL adds 0.3, max 0.8

        # Check for suspicious link patterns
        suspicious_patterns = [
            r"bit\.ly|tinyurl|t\.co|goo\.gl",  # URL shorteners
            r"\.ru|\.cn|\.tk|\.ml|\.ga",  # Suspicious TLDs
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                reasons.append("Contains suspicious link pattern")
                score += 0.2
                break

        return score, reasons

    @staticmethod
    def _check_profanity(content):
        """Check for profanity in content."""
        score = 0.0
        reasons = []

        content_lower = content.lower()
        found_profanity = []

        for word in SpamDetectionService.PROFANITY_LIST:
            if word in content_lower:
                found_profanity.append(word)

        if found_profanity:
            profanity_count = len(found_profanity)
            reasons.append(
                f"Contains {profanity_count} profanity word(s): {', '.join(found_profanity[:3])}"
            )
            score += min(profanity_count * 0.25, 0.7)  # Each profanity adds 0.25, max 0.7

        return score, reasons

    @staticmethod
    def _check_repeat_content(content, user, content_type, store):
        """Check for repeat or similar content."""
        score = 0.0
        reasons = []

        # Simple repeat check - look for exact duplicates in recent content
        cache_key = f"recent_{content_type}s_{user.id}_{store.id if store else 'global'}"
        recent_content = cache.get(cache_key, [])

        # Normalize content for comparison
        normalized_content = SpamDetectionService._normalize_content(content)

        for recent_item in recent_content:
            if normalized_content == recent_item["content"]:
                reasons.append("Exact duplicate of recent content")
                score += 0.5
                break

        # Update cache with new content
        recent_content.append(
            {"content": normalized_content, "timestamp": timezone.now().isoformat()}
        )

        # Keep only last 10 items, expire in 24 hours
        cache.set(cache_key, recent_content[-10:], timeout=86400)

        # Check for excessive similar content from same user
        if len(recent_content) >= 5:
            reasons.append("High volume of content from user")
            score += 0.2

        return score, reasons

    @staticmethod
    def _check_user_patterns(user, content_type, store):
        """Check user submission patterns."""
        score = 0.0
        reasons = []

        # Check submission rate (simple rate limiting)
        rate_key = f"{content_type}_rate_{user.id}_{store.id if store else 'global'}"
        user_rate = cache.get(rate_key, [])

        # Add current timestamp
        current_time = timezone.now()
        user_rate.append(current_time)

        # Keep only submissions in last hour
        cutoff_time = current_time - timezone.timedelta(hours=1)
        user_rate = [t for t in user_rate if t > cutoff_time]

        # Check rate limits
        if len(user_rate) > 10:  # More than 10 submissions per hour
            reasons.append("Excessive submission rate")
            score += 0.4

        # Update cache
        cache.set(rate_key, user_rate, timeout=3600)  # 1 hour

        return score, reasons

    @staticmethod
    def _check_content_patterns(content):
        """Check content patterns and quality indicators."""
        score = 0.0
        reasons = []

        # Check length
        word_count = len(content.split())
        if word_count < 3:
            reasons.append("Content too short")
            score += 0.2
        elif word_count > 500:
            reasons.append("Content suspiciously long")
            score += 0.1

        # Check for excessive caps
        caps_ratio = sum(1 for c in content if c.isupper()) / len(content) if content else 0
        if caps_ratio > 0.3:
            reasons.append("Excessive use of capital letters")
            score += 0.15

        # Check for repetitive patterns
        if re.search(r"(.)\1{4,}", content):  # 5+ repeated characters
            reasons.append("Contains repetitive character patterns")
            score += 0.1

        # Check for nonsensical content (high ratio of non-alphabetic chars)
        alpha_ratio = sum(1 for c in content if c.isalpha()) / len(content) if content else 0
        if alpha_ratio < 0.3 and len(content) > 10:
            reasons.append("Low alphabetic character ratio")
            score += 0.2

        return score, reasons

    @staticmethod
    def _should_auto_reject(score, reasons):
        """Determine if content should be auto-rejected."""
        if score >= 0.8:  # Very high spam score
            return True

        # Check specific auto-reject conditions
        for reason in reasons:
            if "Contains" in reason and "URL" in reason:
                # Extract URL count from reason
                url_match = re.search(r"Contains (\d+) URL", reason)
                if url_match and int(url_match.group(1)) >= SpamDetectionService.AUTO_REJECT_LINKS:
                    return True

            if "Contains" in reason and "profanity" in reason:
                # Extract profanity count from reason
                profanity_match = re.search(r"Contains (\d+) profanity", reason)
                if (
                    profanity_match
                    and int(profanity_match.group(1)) >= SpamDetectionService.AUTO_REJECT_PROFANITY
                ):
                    return True

        return False

    @staticmethod
    def _normalize_content(content):
        """Normalize content for comparison."""
        # Remove whitespace, punctuation, convert to lowercase
        normalized = re.sub(r"[^\w\s]", "", content.lower())
        # Remove extra whitespace
        normalized = " ".join(normalized.split())
        return normalized

    @staticmethod
    def log_spam_attempt(content, user, content_type, spam_result, store=None):
        """Log spam detection attempts for analytics."""
        try:
            # Log to system for monitoring
            logger.warning(
                f"Spam detection: {content_type} by user {user.id} "
                f"- Score: {spam_result['score']:.2f}, "
                f"Recommendation: {spam_result['recommendation']}, "
                f"Reasons: {', '.join(spam_result['reasons'])}"
            )

            # Send notification to moderators if high spam score
            if spam_result["score"] >= 0.7:
                NotificationService.create_notification(
                    user=None,  # System notification to moderators
                    notification_type="spam_detected",
                    title="High spam score detected",
                    message=f"{content_type.title()} with spam score {spam_result['score']:.2f} submitted by {user.get_display_name()}",
                    data={
                        "user_id": user.id,
                        "content_type": content_type,
                        "spam_score": spam_result["score"],
                        "reasons": spam_result["reasons"],
                    },
                    store=store,
                )

        except Exception as e:
            logger.error(f"Failed to log spam attempt: {e}")

    @staticmethod
    def get_spam_stats(store=None, days=7):
        """Get spam detection statistics."""
        # This would query logs/database for spam statistics
        # For now, return placeholder
        return {
            "total_checked": 0,
            "spam_detected": 0,
            "auto_rejected": 0,
            "manual_reviewed": 0,
            "top_reasons": [],
        }
