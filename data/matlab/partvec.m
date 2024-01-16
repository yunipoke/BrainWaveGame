function vec_ = partvec(vec, L)
    if length(vec) > L
        vec_ = vec(end-L+1:end);
    else
        vec_ = vec;
    end
end
