;; How many probes did not reach the target, even once?
;; Which are they? (field prb_id)

;; Data is in https://atlas.ripe.net/api/v1/measurement/1009150/result/

(require "cl-json")

(defun access (object member)
  (cdr (assoc member object)))

(let* ((results (with-open-file (s "1009150.json")
		  (json:decode-json s)))
       (probes (loop for probe in results
		  unless (loop for test in (access probe :result)
			    thereis (access test :rtt))
		  collect probe))
       (unreachable (length probes)))
  (case unreachable
    (0
     (format t "All probes were reachable~%"))
    (1
     (format t "One probe was unreachable~%"))
    (otherwise
     (format t "~D probes were unreachable~%" unreachable)))
  (loop for probe in probes
     do (format t "Probe ~S has a problem~%" (access probe :prb--id))))
