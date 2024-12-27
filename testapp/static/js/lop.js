// Tìm kiếm theo tên lớp
function searchTable() {
    var input = document.getElementById("search-input");
    var filter = input.value.toUpperCase();
    var table = document.getElementById("class-table");
    var rows = table.getElementsByTagName("tr");

    for (var i = 1; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName("td");
        var className = cells[0].textContent || cells[0].innerText;

        if (className.toUpperCase().indexOf(filter) > -1) {
            rows[i].style.display = "";
        } else {
            rows[i].style.display = "none";
        }
    }
}

function filterByGrade() {
    var gradeFilter = document.getElementById("filter-grade").value; // Lấy giá trị từ dropdown
    var rows = document.querySelectorAll("#class-table tbody tr"); // Lấy tất cả các dòng trong bảng

    rows.forEach(function(row) {
        var grade = row.getAttribute("data-grade"); // Lấy giá trị trong thuộc tính data-grade của mỗi dòng
        if (gradeFilter === "" || grade === gradeFilter) { // Nếu bộ lọc trống hoặc khối lớp khớp
            row.style.display = ""; // Hiển thị dòng
        } else {
            row.style.display = "none"; // Ẩn dòng nếu khối lớp không khớp
        }
    });
}


function showStudentList(classId, className) {
    const classListContainer = document.getElementById("class-list-container");
    const studentListContainer = document.getElementById("student-list-container");
    const classTitle = document.querySelector("h1.center-header"); // This targets the header with the class `center-header`
    const tableBody = document.getElementById("student-table-body");

    // Lưu ID lớp hiện tại vào input ẩn
    document.getElementById('current-class-id').value = classId;

    // Cập nhật tiêu đề danh sách lớp với tên lớp hiện tại
    classTitle.innerText = `Danh sách lớp ${className}`;

    // Ẩn danh sách lớp và hiển thị danh sách học sinh
    classListContainer.style.display = "none";
    studentListContainer.style.display = "block";

    // Cuộn lên đầu trang
    window.scrollTo({ top: 0, behavior: "smooth" });

    // Gọi API để tải danh sách học sinh
    fetch(`/lop/${classId}/students`)
        .then(response => response.json())
        .then(data => {
            tableBody.innerHTML = ""; // Xóa dữ liệu cũ

            if (data.students.length === 0) {
                tableBody.innerHTML = "<tr><td colspan='7'>Không có học sinh trong lớp này</td></tr>";
                return;
            }

            // Thêm dữ liệu học sinh
            data.students.forEach((student, index) => {
                const row = `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${student.ho}</td>
                        <td>${student.ten}</td>
                        <td>${student.dob || 'N/A'}</td>
                        <td>${student.sex}</td>
                        <td>${student.address || 'N/A'}</td>
                        <td>
                             <i class="fas fa-trash text-danger" onclick="deleteStudentFromClass(${classId}, ${student.id})" title="Xóa"></i>
                        </td>
                    </tr>
                `;
                tableBody.innerHTML += row;
            });
        })
        .catch(error => {
            console.error("Error loading students:", error);
            tableBody.innerHTML = "<tr><td colspan='7'>Không thể tải danh sách học sinh</td></tr>";
        });
}


function goBackToClassList() {
    const classListContainer = document.getElementById("class-list-container");
    const studentListContainer = document.getElementById("student-list-container");

    // Hiển thị danh sách lớp và ẩn danh sách học sinh
    classListContainer.style.display = "block";
    studentListContainer.style.display = "none";

    // Cuộn lên đầu danh sách lớp
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function showAddStudentModal() {
    fetch('/students/not-in-class') // API trả về danh sách học sinh chưa thuộc lớp
        .then(response => response.json())
        .then(data => {
            const availableStudentList = document.getElementById('available-student-list');
            availableStudentList.innerHTML = "";

            if (data.students.length === 0) {
                availableStudentList.innerHTML = "<tr><td colspan='5'>Không có học sinh khả dụng</td></tr>";
                return;
            }

            data.students.forEach(student => {
                const row = `
                    <tr>
                        <td><input type="checkbox" value="${student.id}" class="student-checkbox"></td>
                        <td>${student.ho}</td>
                        <td>${student.ten}</td>
                        <td>${student.dob || 'N/A'}</td>
                        <td>${student.sex}</td>
                    </tr>
                `;
                availableStudentList.innerHTML += row;
            });

            // Hiển thị modal
            document.getElementById('add-student-modal').style.display = 'block';
        })
        .catch(error => console.error("Error loading students:", error));
}

function closeAddStudentModal() {
    document.getElementById('add-student-modal').style.display = 'none';
}

 function addSelectedStudents() {
    const selectedStudents = []; // Lấy danh sách ID học sinh được chọn
    document.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
        selectedStudents.push(checkbox.value);
    });

    const classId = document.getElementById('current-class-id').value; // ID lớp hiện tại

    fetch('/lop/add-students', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            class_id: classId,
            student_ids: selectedStudents
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            Swal.fire('Thành công!', 'Học sinh đã được thêm vào lớp!', 'success');

            // Đóng modal
            closeAddStudentModal();

            // Gọi lại API để cập nhật danh sách học sinh
            fetch(`/lop/${classId}/students`)
                .then(response => response.json())
                .then(data => {
                    const tableBody = document.getElementById('student-table-body');
                    tableBody.innerHTML = ""; // Xóa danh sách cũ

                    // Hiển thị danh sách học sinh mới
                    data.students.forEach((student, index) => {
                        const row = `
                            <tr>
                                <td>${index + 1}</td>
                                <td>${student.ho}</td>
                                <td>${student.ten}</td>
                                <td>${student.dob || 'N/A'}</td>
                                <td>${student.sex}</td>
                                <td>${student.address || 'N/A'}</td>
                                <td>
                                    <i class="fas fa-trash text-danger" onclick="deleteStudentFromClass(${classId}, ${student.id})" title="Xóa"></i>
                                </td>
                            </tr>
                        `;
                        tableBody.innerHTML += row;
                    });
                })
                .catch(error => {
                    console.error('Error updating student list:', error);
                    Swal.fire('Lỗi!', 'Không thể cập nhật danh sách học sinh.', 'error');
                });
        } else {
            Swal.fire('Lỗi!', data.error || 'Không thể thêm học sinh.', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding students:', error);
        Swal.fire('Lỗi!', 'Không thể xử lý yêu cầu. Vui lòng thử lại.', 'error');
    });
}

function deleteStudentFromClass(classId, studentId) {
    Swal.fire({
        title: 'Bạn có chắc chắn muốn xóa học sinh này khỏi lớp?',
        text: "Hành động này không thể hoàn tác!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Xóa',
        cancelButtonText: 'Hủy'
    }).then((result) => {
        if (result.isConfirmed) {
            // Gửi yêu cầu xóa học sinh khỏi lớp
            fetch(`/lop/${classId}/remove-student/${studentId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire('Thành công!', 'Học sinh đã được xóa khỏi lớp.', 'success');

                    // Gọi lại API để tải danh sách học sinh mới
                    fetch(`/lop/${classId}/students`)
                        .then(response => response.json())
                        .then(data => {
                            const tableBody = document.getElementById('student-table-body');
                            tableBody.innerHTML = ""; // Xóa dữ liệu cũ

                            if (data.students.length === 0) {
                                tableBody.innerHTML = `
                                    <tr>
                                        <td colspan="7" class="text-center text-danger">
                                            Không có học sinh trong lớp này.
                                        </td>
                                    </tr>
                                `;
                            } else {
                                // Hiển thị danh sách học sinh mới
                                data.students.forEach((student, index) => {
                                    const row = `
                                        <tr data-student-id="${student.id}">
                                            <td>${index + 1}</td>
                                            <td>${student.ho}</td>
                                            <td>${student.ten}</td>
                                            <td>${student.dob || 'N/A'}</td>
                                            <td>${student.sex}</td>
                                            <td>${student.address || 'N/A'}</td>
                                            <td>
                                                <i class="fas fa-trash text-danger" onclick="deleteStudentFromClass(${classId}, ${student.id})" title="Xóa"></i>
                                            </td>
                                        </tr>
                                    `;
                                    tableBody.innerHTML += row;
                                });
                            }
                        })
                        .catch(error => {
                            console.error('Error updating student list:', error);
                            Swal.fire('Lỗi!', 'Không thể cập nhật danh sách học sinh.', 'error');
                        });
                } else {
                    Swal.fire('Lỗi!', data.error || 'Không thể xóa học sinh.', 'error');
                }
            })
            .catch(error => {
                console.error('Error removing student:', error);
                Swal.fire('Lỗi!', 'Không thể xử lý yêu cầu. Vui lòng thử lại.', 'error');
            });
        }
    });
}

function loadSiso(lopId) {
    fetch(`/lop/${lopId}/count`)
        .then(response => response.json())
        .then(data => {
            const sisoElement = document.getElementById(`siso-${lopId}`);
            sisoElement.textContent = data.siso;
        })
        .catch(error => {
            console.error("Error fetching class size:", error);
        });
}

document.addEventListener('DOMContentLoaded', () => {
    classes.forEach(c => loadSiso(c.id));
});

