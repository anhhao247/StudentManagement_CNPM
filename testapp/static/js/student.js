    // Hiển thị modal thêm học sinh
    function showAddStudentModal() {
        Swal.fire({
            title: 'Thêm học sinh mới',
            html: `
                <form id="addStudentForm">
                    <div class="mb-3">
                        <label for="ho" class="form-label">Họ</label>
                        <input type="text" id="ho" name="ho" class="form-control" placeholder="Nhập họ" required>
                    </div>
                    <div class="mb-3">
                        <label for="ten" class="form-label">Tên</label>
                        <input type="text" id="ten" name="ten" class="form-control" placeholder="Nhập tên" required>
                    </div>
                    <div class="mb-3">
                        <label for="dob" class="form-label">Ngày sinh</label>
                        <input type="date" id="dob" name="dob" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label for="phone" class="form-label">Số điện thoại</label>
                        <input type="text" id="phone" name="phone" class="form-control" placeholder="Nhập số điện thoại" required>
                    </div>
                    <div class="mb-3">
                        <label for="address" class="form-label">Địa chỉ</label>
                        <input type="text" id="address" name="address" class="form-control" placeholder="Nhập địa chỉ" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" id="email" name="email" class="form-control" placeholder="Nhập email" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Giới tính</label><br>
                        <div class="form-check form-check-inline">
                            <input type="radio" id="male" name="gender" value="Nam" class="form-check-input" checked>
                            <label for="male" class="form-check-label">Nam</label>
                        </div>
                        <div class="form-check form-check-inline">
                            <input type="radio" id="female" name="gender" value="Nữ" class="form-check-input">
                            <label for="female" class="form-check-label">Nữ</label>
                        </div>
                    </div>
                </form>
            `,
            showCancelButton: true,
            confirmButtonText: 'Thêm',
            cancelButtonText: 'Hủy',
            preConfirm: () => {
                const form = document.getElementById("addStudentForm");
                const formData = new FormData(form);

                // Chuyển FormData thành đối tượng JSON
                const studentData = Object.fromEntries(formData);

                // Kiểm tra dữ liệu hợp lệ
                if (!studentData.ho || !studentData.ten || !studentData.dob || !studentData.phone || !studentData.address || !studentData.email) {
                    Swal.showValidationMessage('Vui lòng điền đầy đủ thông tin!');
                    return false;
                }
                return studentData;
            }
        }).then((result) => {
            if (result.isConfirmed) {
                addStudent(result.value); // Gửi dữ liệu tới API
            }
        });
    }
    //model dialog edit student
   function editStudent(studentId, ho, ten, gender , dob,  address ,phone,  email) {
    const formattedDob = formatDate(dob); // Định dạng ngày sinh trước khi gán
    const phoneReadonly = phone ? 'readonly' : ''; // Nếu có sdt, đặt readonly
    const emailReadonly = email ? 'readonly' : ''; // Nếu có email, đặt readonly
    Swal.fire({
        title: 'Chỉnh sửa thông tin học sinh',
        html: `
            <form id="editStudentForm">
                <div class="mb-3">
                    <label for="edit-ho" class="form-label">Họ</label>
                    <input type="text" id="edit-ho" name="ho" class="form-control" value="${ho}" placeholder="Nhập họ" required>
                </div>
                <div class="mb-3">
                    <label for="edit-ten" class="form-label">Tên</label>
                    <input type="text" id="edit-ten" name="ten" class="form-control" value="${ten}" placeholder="Nhập tên" required>
                </div>
                <div class="mb-3">
                    <label for="edit-dob" class="form-label">Ngày sinh</label>
                    <input type="date" id="edit-dob" name="dob" class="form-control" value="${formattedDob}" required>
                </div>
                 <div class="mb-3">
                    <label for="edit-address" class="form-label">Địa chỉ</label>
                    <input type="text" id="edit-address" name="address" class="form-control" value="${address}" placeholder="Nhập địa chỉ" required>
                </div>
                <div class="mb-3">
                    <label for="edit-phone" class="form-label">Số điện thoại</label>
                    <input type="text" id="edit-phone" name="phone" class="form-control" value="${phone}" placeholder="Nhập số điện thoại" required>
                </div>
                <div class="mb-3">
                    <label for="edit-email" class="form-label">Email</label>
                    <input type="email" id="edit-email" name="email" class="form-control" value="${email}" placeholder="Nhập email" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Giới tính</label><br>
                    <div class="form-check form-check-inline">
                        <input type="radio" id="edit-male" name="gender" value="Nam" class="form-check-input" ${
                            gender === 'Nam' ? 'checked' : ''
                        }>
                        <label for="edit-male" class="form-check-label">Nam</label>
                    </div>
                    <div class="form-check form-check-inline">
                        <input type="radio" id="edit-female" name="gender" value="Nữ" class="form-check-input" ${
                            gender === 'Nữ' ? 'checked' : ''
                        }>
                        <label for="edit-female" class="form-check-label">Nữ</label>
                    </div>
                </div>
            </form>
        `,
        showCancelButton: true,
        confirmButtonText: 'Cập nhật',
        cancelButtonText: 'Hủy',
        preConfirm: () => {
            const form = document.getElementById("editStudentForm");
            const formData = new FormData(form);
            const updatedData = Object.fromEntries(formData);

            if (!updatedData.ho || !updatedData.ten || !updatedData.dob || !updatedData.phone || !updatedData.address || !updatedData.email) {
                Swal.showValidationMessage('Vui lòng điền đầy đủ thông tin!');
                return false;
            }
            return updatedData;
        }
    }).then((result) => {
        if (result.isConfirmed) {
            updateStudent(studentId, result.value);
        }
    });
}

//Cập nhật học sinh
function updateStudent(studentId, updatedData) {
    fetch(`/edit_student/${studentId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire(
                'Thành công!',
                'Thông tin học sinh đã được cập nhật!',
                'success'
            ).then(() => location.reload());
        } else {
            Swal.fire('Lỗi!', data.error || 'Đã xảy ra lỗi khi cập nhật học sinh.', 'error');
        }
    })
    .catch(error => {
        Swal.fire('Lỗi!', 'Không thể xử lý yêu cầu. Vui lòng thử lại.', 'error');
        console.error('Error:', error);
    });
}

    function addStudent(studentData) {
    fetch('/them_students', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(studentData)
    })
    .then(response => {
        // Chuyển đổi phản hồi thành JSON ngay cả khi HTTP status là lỗi
        return response.json().then(data => {
            if (!response.ok) {
                // Ném lỗi với thông báo từ server
                throw new Error(data.error || 'Đã xảy ra lỗi không xác định');
            }
            return data;
        });
    })
    .then(data => {
        if (data.success) {
            Swal.fire(
                'Thành công!',
                'Học sinh đã được thêm thành công!',
                'success'
            ).then(() => location.reload());
        }
    })
    .catch(error => {
        Swal.fire(
            'Lỗi!',
            error.message || 'Không thể xử lý yêu cầu. Vui lòng thử lại.',
            'error'
        );
        console.error('Error:', error);
    });
}

//Tìm kiếm học sinh
function searchTable() {
    // Lấy giá trị từ ô tìm kiếm
    const input = document.getElementById("search-input");
    const filter = input.value.toUpperCase(); // Chuyển chữ thường thành chữ in hoa để so sánh không phân biệt chữ hoa/thường
    const table = document.getElementById("student-table"); // Lấy bảng cần tìm kiếm
    const tr = table.getElementsByTagName("tr"); // Lấy tất cả các hàng trong bảng
    let found = false; // Biến để kiểm tra xem có kết quả tìm kiếm hay không

    // Lặp qua tất cả các hàng (trừ hàng đầu tiên là tiêu đề)
    for (let i = 1; i < tr.length; i++) {
        const td = tr[i].getElementsByTagName("td"); // Lấy tất cả các ô trong hàng
        tr[i].style.display = "none"; // Mặc định ẩn hàng

        for (let j = 0; j < td.length; j++) {
            if (td[j]) {
                const textValue = td[j].textContent || td[j].innerText; // Lấy nội dung của ô
                if (textValue.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = ""; // Hiển thị hàng nếu tìm thấy
                    found = true; // Đánh dấu rằng có kết quả
                    break; // Thoát khỏi vòng lặp nội bộ nếu tìm thấy
                }
            }
        }
    }

    // Hiển thị hoặc ẩn thông báo "Không tìm thấy kết quả"
    const noResults = document.getElementById("no-results");
    if (!found) {
        noResults.style.display = "block"; // Hiển thị thông báo
    } else {
        noResults.style.display = "none"; // Ẩn thông báo
    }
}
//Hiển thị dalog sinh viên
    function showEditStudentModal(student) {
    // Gán giá trị hiện tại vào modal
    document.getElementById('edit-ho').value = student.ho;
    document.getElementById('edit-ten').value = student.ten;
    document.getElementById('edit-dob').value = student.dob;
    document.getElementById('edit-phone').value = student.phone;
    document.getElementById('edit-address').value = student.address;
    document.getElementById('edit-email').value = student.email;
    document.querySelector(`input[name="gender"][value="${student.gender}"]`).checked = true;

    // Hiển thị modal
    document.getElementById('edit-student-modal').style.display = 'block';
}

function closeEditStudentModal() {
    document.getElementById('edit-student-modal').style.display = 'none';
}
//Xác nhận xóa học sinh
function deleteStudent(studentId) {
    Swal.fire({
        title: 'Bạn có chắc chắn muốn xóa?',
        text: "Hành động này không thể hoàn tác!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Xóa',
        cancelButtonText: 'Hủy'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/delete_student/${studentId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire(
                        'Đã xóa!',
                        'Học sinh đã được xóa thành công.',
                        'success'
                    ).then(() => location.reload()); // Tải lại trang để cập nhật danh sách
                } else {
                    Swal.fire(
                        'Lỗi!',
                        data.error || 'Không thể xóa học sinh.',
                        'error'
                    );
                }
            })
            .catch(error => {
                Swal.fire(
                    'Lỗi!',
                    'Không thể xử lý yêu cầu. Vui lòng thử lại.',
                    'error'
                );
                console.error('Error:', error);
            });
        }
    });
}


    //Định dạng ngay sinh
    function formatDate(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Thêm số 0 nếu tháng < 10
    const day = String(date.getDate()).padStart(2, '0'); // Thêm số 0 nếu ngày < 10
    return `${year}-${month}-${day}`;
}
 //Phaan trang
let currentPage = 1; // Trang hiện tại
const perPage = 15;  // Số lượng học sinh mỗi trang

function loadStudents(page = 1) {
    fetch(`/students?page=${page}&per_page=${perPage}`)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector("#student-table tbody");
            const paginationContainer = document.getElementById("pagination");

            // Xóa nội dung cũ
            tableBody.innerHTML = "";

            // Thêm học sinh vào bảng
            data.students.forEach((student, index) => {
                const row = `
                    <tr>
                        <td>${(page - 1) * perPage + index + 1}</td>
                        <td>${student.ho}</td>
                        <td>${student.ten}</td>
                        <td>${student.sex}</td>
                        <td>${student.dob}</td>
                        <td>${student.address}</td>
                        <td>${student.sdt}</td>
                        <td>${student.email}</td>
                        <td>
                            <i class="fa fa-edit" onclick="editStudent('${student.id}', '${student.ho}', '${student.ten}', '${student.sex}', '${student.dob}', '${student.address}', '${student.sdt}', '${student.email}')"></i>
                            <i class="fa fa-trash" onclick="deleteStudent('${student.id}')"></i>
                        </td>
                    </tr>
                `;
                tableBody.innerHTML += row;
            });

            // Cập nhật phân trang
            paginationContainer.innerHTML = "";
            for (let i = 1; i <= data.pages; i++) {
                paginationContainer.innerHTML += `
                    <button class="pagination-button ${i === page ? 'active' : ''}" onclick="loadStudents(${i})">${i}</button>
                `;
            }
        })
        .catch(error => console.error('Error loading students:', error));
}

// Gọi hàm loadStudents khi tải trang
loadStudents();
