"""
Unit tests for doctor_panel models.
"""

import pytest
from apps.doctor_panel.models import DoctorNote


@pytest.mark.django_db
class TestDoctorNote:
    """Tests for DoctorNote model."""

    def test_create_doctor_note(self, doctor_user, patient_user):
        """Test creating a doctor note."""
        note = DoctorNote.objects.create(
            doctor=doctor_user,
            patient=patient_user,
            note_type='general',
            content='Patient reported improvement in symptoms.',
            is_private=True,
        )
        assert note.doctor == doctor_user
        assert note.patient == patient_user
        assert note.note_type == 'general'
        assert note.is_private is True

    def test_doctor_note_str(self, doctor_user, patient_user):
        """Test doctor note string representation."""
        note = DoctorNote.objects.create(
            doctor=doctor_user,
            patient=patient_user,
            content='Test note',
        )
        expected = f"Note by Dr. {doctor_user.get_full_name()} for {patient_user.get_full_name()}"
        assert str(note) == expected

    def test_note_types(self, doctor_user, patient_user):
        """Test all note type choices."""
        note_types = ['general', 'follow_up', 'medication_change', 'alert_response']
        for note_type in note_types:
            note = DoctorNote.objects.create(
                doctor=doctor_user,
                patient=patient_user,
                note_type=note_type,
                content=f'Test {note_type}',
            )
            assert note.note_type == note_type

    def test_default_note_type(self, doctor_user, patient_user):
        """Test default note type is general."""
        note = DoctorNote.objects.create(
            doctor=doctor_user,
            patient=patient_user,
            content='Test note without type',
        )
        assert note.note_type == 'general'

    def test_default_is_private(self, doctor_user, patient_user):
        """Test default is_private is True."""
        note = DoctorNote.objects.create(
            doctor=doctor_user,
            patient=patient_user,
            content='Test note',
        )
        assert note.is_private is True

    def test_public_note(self, doctor_user, patient_user):
        """Test creating a public note (shared with patient)."""
        note = DoctorNote.objects.create(
            doctor=doctor_user,
            patient=patient_user,
            content='You are doing great!',
            is_private=False,
        )
        assert note.is_private is False

    def test_multiple_notes_for_patient(self, doctor_user, patient_user):
        """Test doctor can create multiple notes for same patient."""
        DoctorNote.objects.create(
            doctor=doctor_user,
            patient=patient_user,
            content='First note',
        )
        DoctorNote.objects.create(
            doctor=doctor_user,
            patient=patient_user,
            content='Second note',
        )
        notes = DoctorNote.objects.filter(doctor=doctor_user, patient=patient_user)
        assert notes.count() == 2

    def test_notes_ordering(self, doctor_user, patient_user):
        """Test notes are ordered by created_at descending."""
        note1 = DoctorNote.objects.create(
            doctor=doctor_user,
            patient=patient_user,
            content='First note',
        )
        note2 = DoctorNote.objects.create(
            doctor=doctor_user,
            patient=patient_user,
            content='Second note',
        )
        notes = list(DoctorNote.objects.filter(doctor=doctor_user))
        assert notes[0] == note2
        assert notes[1] == note1

    def test_medication_change_note(self, doctor_user, patient_user):
        """Test creating a medication change note."""
        note = DoctorNote.objects.create(
            doctor=doctor_user,
            patient=patient_user,
            note_type='medication_change',
            content='Changed Sumatriptan dosage from 50mg to 100mg due to inefficacy.',
        )
        assert note.note_type == 'medication_change'

    def test_follow_up_note(self, doctor_user, patient_user):
        """Test creating a follow-up note."""
        note = DoctorNote.objects.create(
            doctor=doctor_user,
            patient=patient_user,
            note_type='follow_up',
            content='Scheduled follow-up in 2 weeks to assess medication effectiveness.',
        )
        assert note.note_type == 'follow_up'
