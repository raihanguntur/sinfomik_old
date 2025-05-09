import streamlit as st
from db import get_connection
import time


if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Anda belum login. Mengalihkan ke halaman login...")
    time.sleep(1.5)  # waktu tunggu sebelum redirect (dalam detik)
    st.switch_page("pages/login.py")


else:
    st.title("SINFOMIK - Sistem Informasi Akademik")

    menu = ["Home", "Students", "Grades"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Welcome to SINFOMIK Dashboard!")

    elif choice == "Students":
        st.subheader("Manage Students")
        # Placeholder: students list tables

    elif choice == "Grades": 
        st.subheader("Manage Grades")
        # Placeholder: grades input

    if st.session_state.get("logged_in", False):
    # --- Form to Add New Student ---
        with st.form(key='add_siswa_form'):
            st.subheader("Tambah Siswa Baru")
            
            nisn = st.text_input("NISN", max_chars=10)
            nama = st.text_input("Nama Lengkap")

            submit_button = st.form_submit_button(label="Tambah Siswa")

            if submit_button:
                if nisn and nama:
                    try:
                        with get_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO siswa (nisn, nama) VALUES (%s, %s)", (nisn, nama))
                            conn.commit()
                        st.success(f"Siswa {nama} berhasil ditambahkan!")
                    except Exception as e:
                        st.error(f"Gagal dalam menambahkan siswa: {e}")
                else:
                    st.warning("Mohon isi semua kolom.")

        st.divider()

        # --- Pencarian Siswa ---
        st.subheader("Cari Siswa")
        search_term = st.text_input("Cari berdasarkan NISN atau Nama", "", placeholder="Kosongkan untuk tampilkan semua siswa")

        # --- Students List ---
        st.subheader("Daftar Siswa")

        if "confirm_delete_id" not in st.session_state:
            st.session_state.confirm_delete_id = None


        if "edit_id" not in st.session_state:
            st.session_state.edit_id = None

        try:
            with get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                # Modify SQL to include search term
                if search_term:
                    cursor.execute(
                        "SELECT id, nisn, nama FROM siswa WHERE nisn LIKE %s OR nama LIKE %s ORDER BY id ASC",
                        (f"%{search_term}%", f"%{search_term}%")
                    )
                else:
                    cursor.execute("SELECT id, nisn, nama FROM siswa ORDER BY id ASC")
                siswa_list = cursor.fetchall()

            if siswa_list:
                for siswa in siswa_list:
                    col1, col2, col3, col4 = st.columns([2, 4, 2, 2])
                    
                    with col1:
                        st.write(siswa['nisn'])
                    with col2:
                        st.write(siswa['nama'])
                    with col3:
                        if st.button("✏️ Edit", key=f"edit_{siswa['id']}"):
                            st.session_state.edit_id = siswa['id']
                            st.session_state.edit_nisn = siswa['nisn']
                            st.session_state.edit_nama = siswa['nama']
                            st.session_state.is_editing = True
                            st.rerun()
                    with col4:
                        if st.session_state.confirm_delete_id == siswa['id']:
                            confirm = st.button("✅ Konfirmasi Hapus", key=f"confirm_{siswa['id']}")
                            cancel = st.button("❌ Batal", key=f"cancel_{siswa['id']}")
                            
                            if confirm:
                                with get_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute("DELETE FROM siswa WHERE id = %s", (siswa['id'],))
                                    conn.commit()
                                st.success(f"Siswa {siswa['nama']} berhasil dihapus.")
                                st.session_state.confirm_delete_id = None
                                st.rerun()
                            
                            if cancel:
                                st.session_state.confirm_delete_id = None
                                st.rerun()
                        
                        else:
                            if st.button("🗑️ Hapus", key=f"hapus_{siswa['id']}"):
                                st.session_state.confirm_delete_id = siswa['id']
                                st.rerun()

            else:
                st.info("Belum ada data siswa.")

        except Exception as e:
            st.error(f"Gagal melakukan fetching data siswa: {e}")

        # --- Form Edit Siswa (Popup) ---
        if st.session_state.get("is_editing", False):
            # Creating a modal-like effect for edit form
            with st.expander("Edit Siswa", expanded=True):
                st.subheader("Edit Data Siswa")

                with st.form(key="edit_siswa_form"):
                    nisn_edit = st.text_input("NISN", value=st.session_state.edit_nisn)
                    nama_edit = st.text_input("Nama", value=st.session_state.edit_nama)
                    save_edit = st.form_submit_button("Simpan Perubahan")

                    if save_edit:
                        try:
                            with get_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute(
                                    "UPDATE siswa SET nisn = %s, nama = %s WHERE id = %s",
                                    (nisn_edit, nama_edit, st.session_state.edit_id)
                                )
                                conn.commit()
                            st.success("Data siswa berhasil diperbarui.")
                            # Reset session state to hide the popup
                            st.session_state.is_editing = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal memperbarui data siswa: {e}")

                # Add Cancel Button for Popup
                cancel_button = st.button("❌ Batal", key="cancel_edit")
                if cancel_button:
                    # Hide the form
                    st.session_state.is_editing = False
                    st.rerun()

        # # --- Form Edit Siswa ---
        # if st.session_state.edit_id is not None:
        #     st.divider()
        #     st.subheader("Edit Data Siswa")

        #     with st.form(key="edit_siswa_form"):
        #         nisn_edit = st.text_input("NISN", value=st.session_state.edit_nisn)
        #         nama_edit = st.text_input("Nama", value=st.session_state.edit_nama)
        #         save_edit = st.form_submit_button("Simpan Perubahan")

        #         if save_edit:
        #             try:
        #                 with get_connection() as conn:
        #                     cursor = conn.cursor()
        #                     cursor.execute(
        #                         "UPDATE siswa SET nisn = %s, nama = %s WHERE id = %s",
        #                         (nisn_edit, nama_edit, st.session_state.edit_id)
        #                     )
        #                     conn.commit()
        #                 st.success("Data siswa berhasil diperbarui.")
        #                 st.session_state.edit_id = None
        #                 st.rerun()
        #             except Exception as e:
        #                 st.error(f"Gagal memperbarui data siswa: {e}")
    else:
        st.info("Silakan login untuk mengakses fitur manajemen siswa.")