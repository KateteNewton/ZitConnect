-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 25, 2026 at 01:47 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `zitconnect_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `administrator`
--

CREATE TABLE `administrator` (
  `adminID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `course`
--

CREATE TABLE `course` (
  `courseCode` varchar(15) NOT NULL,
  `courseName` varchar(150) NOT NULL,
  `schoolID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `course`
--

INSERT INTO `course` (`courseCode`, `courseName`, `schoolID`) VALUES
('CS120', 'Introduction to Computer Systems', 1),
('CS130', 'Introduction to Software Engineering', 1),
('CS150', 'Instroduction to Programming', 1),
('CS220', '', 1),
('CS225', 'Operating Systems Concept', 1),
('CS230', 'Software Engineering', 1),
('CS235', 'Database Systems', 1),
('CS250', 'Object Oriented Programming', 1),
('CS270', 'Digital Design', 1),
('CS301', 'Project Management', 1),
('CS320', 'Data Communication and Networking', 1),
('CS345', 'Automata', 1),
('CS350', 'Object Oriented Programming with Java', 1),
('CS351', 'Numerical Analysis', 1),
('CS361', 'Web Programming', 1),
('LA111', 'Communication Skills', 1),
('MA110', 'Mathematical Methods', 1),
('MA210', 'Engineering Mathematics', 1),
('PH110', 'Introcution to Physics', 1),
('PH212', 'General Physics', 1);

-- --------------------------------------------------------

--
-- Table structure for table `program`
--

CREATE TABLE `program` (
  `programID` int(11) NOT NULL,
  `programName` varchar(150) NOT NULL,
  `schoolID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `program`
--

INSERT INTO `program` (`programID`, `programName`, `schoolID`) VALUES
(1, 'Bachelor of Science in Computer Science', 1),
(2, 'Bachelor of Science in Information Systems', 1),
(3, 'Bachelor of Science in Computer Engineering', 1),
(4, 'Bachelor of Science in ICT with Education', 1);

-- --------------------------------------------------------

--
-- Table structure for table `school`
--

CREATE TABLE `school` (
  `schoolID` int(11) NOT NULL,
  `schoolName` varchar(100) NOT NULL,
  `schoolCode` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `school`
--

INSERT INTO `school` (`schoolID`, `schoolName`, `schoolCode`) VALUES
(1, 'School of Information and Communication Technology', 'SICT');

-- --------------------------------------------------------

--
-- Table structure for table `session`
--

CREATE TABLE `session` (
  `sessionID` int(11) NOT NULL,
  `studentID` int(11) NOT NULL,
  `tutorID` int(11) NOT NULL,
  `courseCode` varchar(15) NOT NULL,
  `sessionType` enum('individual','group') NOT NULL DEFAULT 'individual',
  `scheduledDate` date NOT NULL,
  `scheduledTime` time NOT NULL,
  `status` enum('pending','confirmed','declined','completed','cancelled') NOT NULL DEFAULT 'pending',
  `createdAt` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `student`
--

CREATE TABLE `student` (
  `studentID` int(11) NOT NULL,
  `programID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tutor`
--

CREATE TABLE `tutor` (
  `tutorID` int(11) NOT NULL,
  `verificationStatus` enum('pending','approved','rejected') NOT NULL DEFAULT 'pending',
  `averageRating` decimal(3,2) NOT NULL DEFAULT 0.00,
  `bio` varchar(500) DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tutorcourse`
--

CREATE TABLE `tutorcourse` (
  `tutorCourseID` int(11) NOT NULL,
  `tutorID` int(11) NOT NULL,
  `courseCode` varchar(15) NOT NULL,
  `gradeObtained` varchar(5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `userID` int(11) NOT NULL,
  `fullName` varchar(100) NOT NULL,
  `userName` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('student','tutor','admin') NOT NULL,
  `profilePicture` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`userID`, `fullName`, `userName`, `email`, `password`, `role`, `profilePicture`) VALUES
(1, 'Newton I Katete', 'newtonisaackatete@gmail.com', 'newtonisaackatete@gmail.com', '123456', 'tutor', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `verificationdocument`
--

CREATE TABLE `verificationdocument` (
  `documentID` int(11) NOT NULL,
  `tutorID` int(11) NOT NULL,
  `documentType` enum('result_slip','transcript') NOT NULL,
  `filePath` varchar(255) NOT NULL,
  `uploadDate` datetime NOT NULL DEFAULT current_timestamp(),
  `approvalStatus` enum('pending','approved','rejected') NOT NULL DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `administrator`
--
ALTER TABLE `administrator`
  ADD PRIMARY KEY (`adminID`);

--
-- Indexes for table `course`
--
ALTER TABLE `course`
  ADD PRIMARY KEY (`courseCode`),
  ADD KEY `fk_course_school` (`schoolID`);

--
-- Indexes for table `program`
--
ALTER TABLE `program`
  ADD PRIMARY KEY (`programID`),
  ADD KEY `fk_program_school` (`schoolID`);

--
-- Indexes for table `school`
--
ALTER TABLE `school`
  ADD PRIMARY KEY (`schoolID`),
  ADD UNIQUE KEY `uq_schoolCode` (`schoolCode`);

--
-- Indexes for table `session`
--
ALTER TABLE `session`
  ADD PRIMARY KEY (`sessionID`),
  ADD KEY `fk_session_student` (`studentID`),
  ADD KEY `fk_session_tutor` (`tutorID`),
  ADD KEY `fk_session_course` (`courseCode`);

--
-- Indexes for table `student`
--
ALTER TABLE `student`
  ADD PRIMARY KEY (`studentID`),
  ADD KEY `fk_student_program` (`programID`);

--
-- Indexes for table `tutor`
--
ALTER TABLE `tutor`
  ADD PRIMARY KEY (`tutorID`);

--
-- Indexes for table `tutorcourse`
--
ALTER TABLE `tutorcourse`
  ADD PRIMARY KEY (`tutorCourseID`),
  ADD UNIQUE KEY `uq_tutor_course` (`tutorID`,`courseCode`),
  ADD KEY `fk_tutorcourse_course` (`courseCode`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`userID`),
  ADD UNIQUE KEY `userName` (`userName`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `verificationdocument`
--
ALTER TABLE `verificationdocument`
  ADD PRIMARY KEY (`documentID`),
  ADD KEY `fk_verdoc_tutor` (`tutorID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `program`
--
ALTER TABLE `program`
  MODIFY `programID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `school`
--
ALTER TABLE `school`
  MODIFY `schoolID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `session`
--
ALTER TABLE `session`
  MODIFY `sessionID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tutorcourse`
--
ALTER TABLE `tutorcourse`
  MODIFY `tutorCourseID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `userID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `verificationdocument`
--
ALTER TABLE `verificationdocument`
  MODIFY `documentID` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `administrator`
--
ALTER TABLE `administrator`
  ADD CONSTRAINT `fk_administrator_user` FOREIGN KEY (`adminID`) REFERENCES `user` (`userID`);

--
-- Constraints for table `course`
--
ALTER TABLE `course`
  ADD CONSTRAINT `fk_course_school` FOREIGN KEY (`schoolID`) REFERENCES `school` (`schoolID`);

--
-- Constraints for table `program`
--
ALTER TABLE `program`
  ADD CONSTRAINT `fk_program_school` FOREIGN KEY (`schoolID`) REFERENCES `school` (`schoolID`);

--
-- Constraints for table `session`
--
ALTER TABLE `session`
  ADD CONSTRAINT `fk_session_course` FOREIGN KEY (`courseCode`) REFERENCES `course` (`courseCode`),
  ADD CONSTRAINT `fk_session_student` FOREIGN KEY (`studentID`) REFERENCES `student` (`studentID`),
  ADD CONSTRAINT `fk_session_tutor` FOREIGN KEY (`tutorID`) REFERENCES `tutor` (`tutorID`);

--
-- Constraints for table `student`
--
ALTER TABLE `student`
  ADD CONSTRAINT `fk_student_program` FOREIGN KEY (`programID`) REFERENCES `program` (`programID`),
  ADD CONSTRAINT `fk_student_user` FOREIGN KEY (`studentID`) REFERENCES `user` (`userID`);

--
-- Constraints for table `tutor`
--
ALTER TABLE `tutor`
  ADD CONSTRAINT `fk_tutor_user` FOREIGN KEY (`tutorID`) REFERENCES `user` (`userID`);

--
-- Constraints for table `tutorcourse`
--
ALTER TABLE `tutorcourse`
  ADD CONSTRAINT `fk_tutorcourse_course` FOREIGN KEY (`courseCode`) REFERENCES `course` (`courseCode`),
  ADD CONSTRAINT `fk_tutorcourse_tutor` FOREIGN KEY (`tutorID`) REFERENCES `tutor` (`tutorID`);

--
-- Constraints for table `verificationdocument`
--
ALTER TABLE `verificationdocument`
  ADD CONSTRAINT `fk_verdoc_tutor` FOREIGN KEY (`tutorID`) REFERENCES `tutor` (`tutorID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
